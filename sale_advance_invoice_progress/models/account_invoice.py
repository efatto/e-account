# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    @api.depends('price_subtotal')
    def _get_price_subtotal_signed(self):
        for line in self:
            line.price_subtotal_signed = line.price_subtotal * (
                -1 if line.invoice_id.type in ['out_refund', 'in_refund'] else
                1)

    advance_invoice_id = fields.Many2one('account.invoice', 'Advance invoice')
    price_subtotal_signed = fields.Float(compute=_get_price_subtotal_signed)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.returns('self')
    def refund(self, date=None, period_id=None, description=None,
               journal_id=None):
        new_invoices = super(AccountInvoice, self).refund(
            date=date, period_id=period_id, description=description,
            journal_id=journal_id)
        for invoice in self:
            order = self.env['sale.order'].search(
                    [('invoice_ids', 'in', [invoice.id])])
            # invoice has order origin, so link the new one created
            # no other checks like advance invoice
            if len(new_invoices) > 1:
                _logger.debug('More than 1 invoice created from refund')
            for new_invoice in new_invoices:
                order.write(
                    {'invoice_ids': [(4, new_invoice.id)]})
        return new_invoices
