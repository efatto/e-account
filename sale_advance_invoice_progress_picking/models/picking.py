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
        invoice_id_picking_ids = {}
        for move in moves:
            for invoice in move.picking_id.sale_id.invoice_ids:
                if invoice.id in invoice_ids:
                    if invoice not in invoice_id_picking_ids:
                        invoice_id_picking_ids = {invoice: [move.picking_id]}
                    elif move.picking_id not in invoice_id_picking_ids[invoice]:
                        invoice_id_picking_ids[invoice].append(move.picking_id)

        order_invoiced_amount = {}
        order_invoice = {}
        if invoice_id_picking_ids:
            for invoice_id, picking_ids in invoice_id_picking_ids.items():
                for picking_id in picking_ids:
                    # take only not advance invoice lines
                    for line in invoice_id.invoice_line.filtered(
                        lambda x: not x.advance_invoice_id
                    ):
                        # take only invoice lines originated from picking
                        if picking_id.name == line.origin or \
                                picking_id.origin == line.origin:
                            if picking_id.sale_id not in order_invoiced_amount:
                                order_invoiced_amount[picking_id.sale_id] = \
                                    line.price_subtotal
                            else:
                                order_invoiced_amount[picking_id.sale_id] += \
                                    line.price_subtotal
                    if invoice_id not in order_invoice:
                        order_invoice[invoice_id] = {
                            picking_id.sale_id: order_invoiced_amount[
                                picking_id.sale_id]}
                    if picking_id.sale_id not in order_invoice[invoice_id]:
                        order_invoice[invoice_id].update(
                            {picking_id.sale_id: order_invoiced_amount[
                                picking_id.sale_id]})

                    for advance_invoice in picking_id.sale_id.advance_invoice_ids:
                        for preline in advance_invoice.invoice_line:
                            inv_line_id = self.pool[
                                'account.invoice.line'].copy(
                                cr, uid, preline.id, {
                                    'invoice_id': invoice_id.id,
                                    'price_unit': - order_invoice[invoice_id]
                                    [picking_id.sale_id] *
                                    picking_id.sale_id.advance_percentage / 100 *
                                    preline.price_subtotal /
                                    picking_id.sale_id.advance_amount,
                                    'advance_invoice_id': advance_invoice.id,
                                })
                        invoice_obj.button_compute(
                            cr, uid, [invoice_id.id], context=context,
                            set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoice_ids
