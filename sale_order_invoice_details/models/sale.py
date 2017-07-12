# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models


class InvoiceSaleOrder(models.Model):
    _name = 'invoice.sale.order'
    _description = 'Invoice from sale order'

    name = fields.Char()
    amount_invoice = fields.Float()
    amount_product = fields.Float()
    amount_contribution = fields.Float()
    amount_transport = fields.Float()
    amount_other = fields.Float()
    amount_invoice_not_found = fields.Float()
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Account Invoice',
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_invoiced_amount_from_picking(self):
        for order in self:
            amount_invoice = amount_invoice_not_found = amount_contribution = \
                amount_product = amount_transport = amount_other = 0.0
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    values = {
                        'name': invoice.name,
                        'order_id': order.id,
                        'invoice_id': invoice.id,
                        'amount_invoice': 0.0,
                        'amount_contribution': 0.0,
                        'amount_product': 0.0,
                        'amount_transport': 0.0,
                        'amount_other': 0.0,
                    }
                    for line in invoice.invoice_line:
                        if invoice.stock_picking_package_preparation_ids:
                            for sppp in invoice.\
                                    stock_picking_package_preparation_ids:
                                for picking in sppp.picking_ids:
                                    if line.origin and \
                                            order.name in picking.origin and (
                                            line.origin in picking.origin or
                                            line.origin in picking.name):
                                        amount_invoice += line.price_subtotal
                                        if line.product_id:
                                            if line.product_id.is_contribution:
                                                amount_contribution += line.price_subtotal
                                            elif line.product_id.is_transport:
                                                amount_transport += line.price_subtotal
                                            elif line.product_id.is_other:
                                                amount_other += line.price_subtotal
                                            else: # discount is here too
                                                amount_product += line.price_subtotal
                                        else: # not product defined
                                            amount_other += line.price_subtotal
                        else:
                            if line.origin and line.origin in order.name:
                                amount_invoice += line.price_subtotal
                                if line.product_id:
                                    if line.product_id.is_contribution:
                                        amount_contribution += line.price_subtotal
                                    elif line.product_id.is_transport:
                                        amount_transport += line.price_subtotal
                                    elif line.product_id.is_other:
                                        amount_other += line.price_subtotal
                                    else:  # discount is here too
                                        amount_product += line.price_subtotal
                                else:  # not product defined
                                    amount_other += line.price_subtotal
                            else:
                                amount_invoice_not_found += line.price_subtotal
                    values.update({
                        'amount_invoice': amount_invoice,
                        'amount_contribution': amount_contribution,
                        'amount_product': amount_product,
                        'amount_transport': amount_transport,
                        'amount_other': amount_other,
                        'amount_invoice_not_found': amount_invoice_not_found,
                    })
                    if order.invoice_sale_order_ids:
                        for invoice_order_id in order.invoice_sale_order_ids:
                            if invoice_order_id.order_id == order and \
                                    invoice_order_id.invoice_id == invoice:
                                invoice_order_id.write(values)
                    else:
                        res = self.env['invoice.sale.order'].create(values)
                        order.invoice_sale_order_ids = res

    invoice_sale_order_ids = fields.One2many(
        comodel_name='invoice.sale.order',
        inverse_name='order_id',
        string='Related invoices',
        compute=_get_invoiced_amount_from_picking)
