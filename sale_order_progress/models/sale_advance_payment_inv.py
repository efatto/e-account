from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


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
                if self.order_progress_id.is_advance:
                    self.advance_payment_method = "fixed"
                    self.amount = self.order_progress_id.residual_toinvoice
                else:
                    self.advance_payment_method = "all"

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        res = super().onchange_advance_payment_method()
        if (
            self.advance_payment_method == 'percentage'
            and self.order_progress_id
            and self.order_progress_id.is_advance
        ):
            amount = self.order_progress_id.amount_percent
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
    amount_advance_toreturn = fields.Float(
        digits=dp.get_precision('Account'),
        help='Amount of the advance to return',
    )

    @api.onchange("order_progress_id")
    def _onchange_order_progress_id(self):
        if self.order_progress_id:
            self.amount_advance_toreturn = (
                self.order_progress_id.amount_advance_toreturn)

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        if (
            self.advance_payment_method == "all"
            and self.amount_advance_toreturn
        ):
            vals_to_return = order.get_amount_advance_toreturn_by_line(
                self.amount_advance_toreturn)
            if vals_to_return:
                self = self.with_context(amount_advance_toreturn=vals_to_return)
        invoice = super()._create_invoice(order, so_line, amount)
        if self.order_progress_id:
            invoice.invoice_line_ids.write(
                {"sale_order_progress_id": self.order_progress_id.id})
        return invoice

    @api.multi
    def create_invoices(self):
        if (
            self.advance_payment_method == "all"
            and self.amount_advance_toreturn
        ):
            orders = self.env['sale.order'].browse(
                self.env.context.get('active_ids', [])
            )
            vals_to_return = orders.get_amount_advance_toreturn_by_line(
                self.amount_advance_toreturn)
            if vals_to_return:
                self = self.with_context(amount_advance_toreturn=vals_to_return)
        if self.order_progress_id:
            return super(
                SaleAdvancePaymentInv,
                self.with_context(sale_order_progress_id=self.order_progress_id.id)
            ).create_invoices()
        return super().create_invoices()
