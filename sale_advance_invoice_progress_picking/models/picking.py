# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.cr_uid_context
    def _invoice_create_line(
        self, cr, uid, moves, journal_id, inv_type='out_invoice',
            context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = super(StockPicking, self)._invoice_create_line(
            cr, uid, moves, journal_id, inv_type=inv_type, context=context)
        picking_invoices = {}
        for move in moves:
            for invoice in move.picking_id.sale_id.invoice_ids:
                if invoice.id in invoice_ids:
                    picking_invoices[invoice] = move.picking_id
        order_invoiced_amount = {}
        order_invoice = {}
        if picking_invoices:
            for invoice, picking in picking_invoices.items():
                for line in invoice.invoice_line:
                    if line.advance_invoice_id in \
                            picking.sale_id.advance_invoice_ids:
                        continue
                    if picking.sale_id not in order_invoiced_amount:
                        order_invoiced_amount[picking.sale_id] = \
                            line.price_subtotal
                    else:
                        order_invoiced_amount[picking.sale_id] += \
                            line.price_subtotal
                if invoice not in order_invoice:
                    order_invoice[invoice] = {
                        picking.sale_id: order_invoiced_amount[
                            picking.sale_id]}
                if picking.sale_id not in order_invoice[invoice]:
                    order_invoice[invoice].update(
                        {picking.sale_id: order_invoiced_amount[
                            picking.sale_id]})

                for advance_invoice in picking.sale_id.advance_invoice_ids:
                    for preline in advance_invoice.invoice_line:
                        inv_line_id = self.pool[
                            'account.invoice.line'].copy(
                            cr, uid, preline.id, {
                                'invoice_id': invoice.id,
                                'price_unit': - order_invoice[invoice]
                                [picking.sale_id] *
                                picking.sale_id.advance_percentage / 100 *
                                preline.price_subtotal /
                                picking.sale_id.advance_amount,
                                'advance_invoice_id': advance_invoice.id,
                            })
                    invoice_obj.button_compute(
                        cr, uid, [invoice.id], context=context,
                        set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoice_ids
