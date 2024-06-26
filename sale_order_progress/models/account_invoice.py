from odoo import api, models, fields


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_order_progress_id = fields.Many2one(
        comodel_name="sale.order.progress",
        ondelete="restrict",
        string='Sale order progress',
    )
    sale_order_ids = fields.Many2many(
        compute="_compute_sale_order_ids",
        comodel_name="sale.order",
        store=True,
        string="Sale orders",
        groups="account.group_account_invoice"
    )

    @api.multi
    def _compute_sale_order_ids(self):
        for line in self:
            if line.sale_line_ids:
                line.sale_order_ids = line.mapped("sale_line_ids.order_id")
            else:
                line.sale_order_ids = False
