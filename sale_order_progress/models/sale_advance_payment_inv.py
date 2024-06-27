from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_orders(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        return sale_orders

    @api.onchange('order_progress_id')
    def _onchange_order_progress_id(self):
        if self._count() == 1:
            if self.order_progress_id:
                if self.order_progress_id.amount_percent:
                    self.advance_payment_method = "percentage"
                    self.amount = self.order_progress_id.amount_percent
                elif self.order_progress_id.amount_toinvoice_manual:
                    self.advance_payment_method = "fixed"
                    self.amount = self.order_progress_id.amount_toinvoice_manual
                else:
                    self.advance_payment_method = "all"

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        res = super().onchange_advance_payment_method()
        if self.advance_payment_method == 'percentage':
            amount = self.order_progress_id.amount_percent \
                if self.order_progress_id.amount_percent else 0
            return {'value': {'amount': amount}}
        return res

    @api.model
    def _default_has_progress(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        if any(order.order_progress_ids for order in sale_orders):
            return True
        return False

    has_progress = fields.Boolean(
        string='Has Progress',
        default=_default_has_progress,
    )
    order_ids = fields.Many2many(
        comodel_name='sale.order',
        default=_get_orders,
    )
    order_progress_id = fields.Many2one(
        comodel_name="sale.order.progress",
        string='Order Progress',
        help='Select order progress line to link to the invoice line'
    )

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super()._create_invoice(order, so_line, amount)
        if self.order_progress_id:
            invoice.invoice_line_ids.write(
                {"sale_order_progress_id": self.order_progress_id.id})
        return invoice

    @api.multi
    def create_invoices(self):
        if self.order_progress_id:
            return super(
                SaleAdvancePaymentInv,
                self.with_context(sale_order_progress_id=self.order_progress_id.id)
            ).create_invoices()
        return super().create_invoices()
