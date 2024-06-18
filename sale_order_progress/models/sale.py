from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
    amount_toinvoice_difference = fields.Monetary(
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
            if order.order_progress_ids:
                order.amount_percent_total = sum(order.mapped(
                    "order_progress_ids.amount_percent"
                ))
                amount_toinvoice_total = sum(order.mapped(
                    "order_progress_ids.amount_toinvoice"
                ))
                order.amount_toinvoice_total = amount_toinvoice_total
                order.amount_toinvoice_difference = (
                    amount_toinvoice_total - order.amount_untaxed)
            else:
                order.amount_percent_total = 0
                order.amount_toinvoice_total = 0
                order.amount_toinvoice_difference = 0

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
