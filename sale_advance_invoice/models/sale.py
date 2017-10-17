# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_order_lines(self):
        line_ids = self.env['sale.order'].browse(
            self._context['active_id']).order_line
        return line_ids

    @api.model
    def _get_advance_product(self):
        line_ids = self.env['sale.order'].browse(
            self._context['active_id']).order_line
        if line_ids and line_ids[0].product_id:
            return line_ids[0].product_id
        else:
            return super(SaleAdvancePaymentInv, self)._get_advance_product()

    order_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        relation='advance_sale_order_line_rel',
        column1='order_line_id', column2='advance_id',
        string='Order lines',
        default=_get_order_lines,
        help='Select order lines to print details in invoice'
    )
    product_id = fields.Many2one(
        default=_get_advance_product,
    )

    @api.multi
    def create_invoices(self):
        """ create invoices for the active sales orders """
        for order in self:
            if order.advance_payment_method in ('fixed', 'percentage'):
                inv_ids = []
                for sale_id, inv_values in order._prepare_advance_invoice_vals():
                    inv_ids.append(order._create_invoices(inv_values, sale_id))
                for inv in self.env['account.invoice'].browse(inv_ids):
                    if order.order_line_ids:
                        description = ''
                        for line in order.order_line_ids:
                            description += ('\n' + line.name)
                    for invoice_line in inv.invoice_line:
                        invoice_line.name = \
                            order.with_context({
                              'lang': order.order_line_ids.order_id.partner_id.lang}
                            )._translate_advance(percentage=True) % (
                              order.amount) + description
                if order._context.get('open_invoices', False):
                    return order.open_invoices(inv_ids)
                return {'type': 'ir.actions.act_window_close'}
            else:
                return super(SaleAdvancePaymentInv, order).create_invoices()
