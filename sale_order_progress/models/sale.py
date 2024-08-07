from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero
import re


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_progress_ids = fields.One2many(
        comodel_name='sale.order.progress',
        inverse_name='order_id',
        string='Order Progress',
    )
    amount_percent_total = fields.Float(
        compute="_compute_totals",
        store=True,
    )
    amount_toinvoice_total = fields.Monetary(
        compute="_compute_totals",
        store=True,
    )
    amount_advance_toreturn_total = fields.Monetary(
        compute="_compute_totals",
        store=True,
    )
    amount_toinvoice_difference = fields.Monetary(
        compute="_compute_totals",
        store=True,
    )
    date_progress_end = fields.Date(
        string="Expected end date",
    )
    total_advance_amount = fields.Monetary(
        compute="_compute_total_advance_percent",
    )
    total_advance_percent = fields.Float(
        string="Total advance (%)",
        compute="_compute_total_advance_percent",
    )

    def get_amount_advance_toreturn_by_line(self, amount_advance_toreturn):
        for order in self:
            res = {}
            downpayment_lines = order.order_line.filtered("is_downpayment")
            if not downpayment_lines:
                return res
            # compute amount advance to return for lines only when it is lower than
            # the total advance
            total_advance_amount = sum(downpayment_lines.mapped("price_unit"))
            if amount_advance_toreturn < total_advance_amount:
                for line in downpayment_lines:
                    if float_compare(
                        amount_advance_toreturn,
                        line.price_unit,
                        precision_rounding=line.currency_id.rounding,
                    ) == -1:
                        res[line] = amount_advance_toreturn
                        break
                    elif float_compare(
                        amount_advance_toreturn,
                        line.price_unit,
                        precision_rounding=line.currency_id.rounding,
                    ) == 0:
                        res[line] = line.price_unit
                        break
                    elif float_compare(
                        amount_advance_toreturn,
                        line.price_unit,
                        precision_rounding=line.currency_id.rounding,
                    ) == 1:
                        res[line] = line.price_unit
                        amount_advance_toreturn -= line.price_unit
            return res

    @api.multi
    def update_difference(self):
        for order in self:
            order._compute_totals()

    @api.multi
    @api.depends(
        "amount_total",
        "order_progress_ids.amount_toinvoice",
        "order_progress_ids.is_advance",
    )
    def _compute_total_advance_percent(self):
        for order in self:
            if order.order_progress_ids:
                total_advance_amount = sum(
                    order.order_progress_ids.filtered(
                        lambda x: x.is_advance
                    ).mapped("amount_toinvoice")
                    or [0]
                )
                total_advance_percent = 0
                if total_advance_amount:
                    total_advance_percent = (
                        total_advance_amount / order.amount_total * 100.0
                    )
                order.total_advance_amount = total_advance_amount
                order.total_advance_percent = total_advance_percent
            else:
                order.total_advance_percent = 0
                order.total_advance_amount = 0

    @api.multi
    @api.depends(
        "order_progress_ids.amount_percent",
        "order_progress_ids.amount_toinvoice",
        "order_progress_ids.amount_advance_toreturn",
        "amount_total",
    )
    def _compute_totals(self):
        for order in self:
            if order.order_progress_ids:
                order.amount_percent_total = sum(
                    order.order_progress_ids.filtered(
                        lambda op: not op.is_advance
                    ).mapped(
                        "amount_percent"
                    )
                )
                amount_toinvoice_total = sum(order.mapped(
                    "order_progress_ids.amount_toinvoice"
                ))
                order.amount_toinvoice_total = amount_toinvoice_total
                amount_advance_toreturn_total = sum(order.mapped(
                    "order_progress_ids.amount_advance_toreturn"
                ))
                order.amount_advance_toreturn_total = amount_advance_toreturn_total
                order.amount_toinvoice_difference = (
                    amount_toinvoice_total
                    - amount_advance_toreturn_total
                    - order.amount_total
                )
            else:
                order.amount_percent_total = 0
                order.amount_toinvoice_total = 0
                order.amount_advance_toreturn_total = 0
                order.amount_toinvoice_difference = 0

    @api.multi
    @api.constrains(
        'amount_percent_total',
        'amount_toinvoice_total',
        'amount_total',
        'amount_advance_toreturn_total',
    )
    def check_amount_percent_total(self):
        for order in self:
            if order.amount_percent_total > 100:
                raise ValidationError(_(
                    "Total of order progress percent cannot exceed 100!"
                ))
            if float_compare(
                order.amount_toinvoice_total - max(
                    order.total_advance_amount,
                    sum(
                        order.mapped(
                            "order_progress_ids.amount_advance_toreturn"
                        )
                    )
                ),
                order.amount_total,
                precision_rounding=order.currency_id.rounding
            ) == 1:
                raise ValidationError(_(
                    "Total of progress amount to invoice cannot exceed order amount!"
                ))

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super().action_invoice_create(grouped=grouped, final=final)
        if self._context.get("sale_order_progress_id"):
            for invoice in self.env["account.invoice"].browse(invoice_ids):
                invoice.invoice_line_ids.write({
                    "sale_order_progress_id": self._context["sale_order_progress_id"],
                })
        return invoice_ids


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    invoice_progress_ids = fields.Many2many(
        comodel_name='sale.order.progress',
        compute="_compute_invoice_progress_ids",
        store=True,
    )

    @api.depends("invoice_lines.sale_order_progress_id")
    @api.multi
    def _compute_invoice_progress_ids(self):
        for line in self:
            if line.invoice_lines and line.mapped(
                "invoice_lines.sale_order_progress_id"
            ):
                line.invoice_progress_ids = line.mapped(
                    "invoice_lines.sale_order_progress_id"
                )
            else:
                line.invoice_progress_ids = False

    @staticmethod
    def desc_nocode(string):
        return re.compile("\[.*\] ").sub('', string)  # pylint: disable=W1401

    def invoice_line_create_vals(self, invoice_id, qty):
        # Override to create refund for down payment lines with maximum value requested
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        amount_advance_toreturn = self.env.context.get("amount_advance_toreturn", {})
        if amount_advance_toreturn:
            down_payment_lines = self.filtered("is_downpayment")
            if down_payment_lines:
                self -= down_payment_lines
            vals_list = super().invoice_line_create_vals(invoice_id, qty)
            for line in down_payment_lines:
                if (
                    not float_is_zero(qty, precision_digits=precision)
                    or not line.product_id
                ):
                    vals = line._prepare_invoice_line(qty=qty)
                    amount_advance_toreturn = self.env.context["amount_advance_toreturn"]
                    price_unit = line.price_unit
                    if line in amount_advance_toreturn:
                        price_unit = amount_advance_toreturn[line]
                    else:
                        # this down payment line has not to be returned, todo delete it
                        price_unit = 0
                    vals.update({
                        'price_unit': price_unit,
                        'invoice_id': invoice_id,
                        'sale_line_ids': [(6, 0, [line.id])]
                    })
                    vals_list.append(vals)
        else:
            vals_list = super().invoice_line_create_vals(invoice_id, qty)
        return vals_list
