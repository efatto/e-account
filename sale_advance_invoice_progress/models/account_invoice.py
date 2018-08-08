# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _get_price_subtotal_signed(self):
        sign = +1
        for line in self:
            if line.invoice_id.type in ['out_refund', 'in_refund']:
                sign = -1
            line.price_subtotal_signed = line.price_subtotal * sign

    advance_invoice_id = fields.Many2one('account.invoice', 'Advance invoice')
    price_subtotal_signed = fields.Float(compute=_get_price_subtotal_signed)
