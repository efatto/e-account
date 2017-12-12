# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


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
                    elif move.picking_id not in \
                            invoice_id_picking_ids[invoice]:
                        invoice_id_picking_ids[invoice].append(move.picking_id)

        order_invoiced_amount = {}
        if invoice_id_picking_ids:
            for invoice_id, picking_ids in invoice_id_picking_ids.items():
                invoice_lines = invoice_id.invoice_line.filtered(
                    lambda x: not x.advance_invoice_id)
                for line in invoice_lines:
                    for picking_id in picking_ids:
                        if picking_id.name == line.origin or \
                                picking_id.origin == line.origin:
                            if picking_id.sale_id not in order_invoiced_amount:
                                order_invoiced_amount[picking_id.sale_id] = \
                                    line.price_subtotal
                                break
                            else:
                                order_invoiced_amount[picking_id.sale_id] += \
                                    line.price_subtotal
                                break
                total_return_amount = 0
                for sale_id in order_invoiced_amount.keys():
                    for advance_invoice in sale_id.advance_invoice_ids:
                        if advance_invoice.state == 'cancel':
                            return False
                        if advance_invoice.state not in ['paid']:
                            raise exceptions.ValidationError(
                                _('Advance invoice %s of %s sale order must be'
                                  ' in state paid to be returned.') %
                                (advance_invoice.number, sale_id.name)
                            )
                        for preline in advance_invoice.invoice_line:
                            return_amount = (
                                order_invoiced_amount[sale_id]
                                * sale_id.advance_percentage /
                                100 * preline.price_subtotal /
                                sale_id.advance_amount)
                            self.pool[
                                'account.invoice.line'].copy(
                                cr, uid, preline.id, {
                                    'invoice_id': invoice_id.id,
                                    'price_unit': - return_amount,
                                    'advance_invoice_id': advance_invoice.id,
                                    'sequence': 0,
                                    'name': (_('Ref. %s nr. %s ') % (
                                                advance_invoice.journal_id.
                                                advance_description,
                                                advance_invoice.number))
                                })
                            total_return_amount += return_amount
                        invoice_obj.button_compute(
                            cr, uid, [invoice_id.id], context=context,
                            set_total=(inv_type in (
                                'in_invoice', 'in_refund')))
        return invoice_ids
