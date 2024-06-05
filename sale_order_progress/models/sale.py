from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


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
    amount_toinvoice_total = fields.Float(
        compute="_compute_totals",
        store=True,
    )
    is_amount_toinvoice_under_total = fields.Boolean(
        compute="_compute_totals",
        store=True,
    )

    @api.multi
    @api.depends(
        "order_progress_ids.amount_percent",
        "order_progress_ids.amount_toinvoice",
        "amount_untaxed",
    )
    def _compute_totals(self):
        for order in self:
            order.amount_percent_total = sum(order.mapped(
                "order_progress_ids.amount_percent"
            ))
            amount_toinvoice_total = sum(order.mapped(
                "order_progress_ids.amount_toinvoice"
            ))
            order.amount_toinvoice_total = amount_toinvoice_total
            order.is_amount_toinvoice_under_total = True if float_compare(
                amount_toinvoice_total,
                order.amount_untaxed,
                precision_rounding=order.currency_id.rounding
            ) == -1 else False

    @api.multi
    @api.constrains('amount_percent_total', 'amount_toinvoice_total', 'amount_untaxed')
    def check_amount_percent_total(self):
        for order in self:
            if order.amount_percent_total > 100:
                raise ValidationError(_(
                    "Total of order progress percent cannot exceed 100!"
                ))
            if order.amount_toinvoice_total > order.amount_untaxed:
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

    order_progress_id = fields.Many2one(
        "sale.order.progress",
    )
