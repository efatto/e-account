# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    bank_riba_id = fields.Many2one('res.bank', 'Bank for ri.ba.')

    @api.cr_uid_ids_context
    def onchange_partner_id(
            self, cr, uid, ids, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False,
            context=None):
        result = super(AccountInvoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice, payment_term,
            partner_bank_id, company_id, context)

        partner = self.pool['res.partner'].browse(
            cr, uid, partner_id, context)
        if partner.bank_riba_id:
            result['value']['bank_riba_id'] = partner.bank_riba_id.id
        else:
            result['value']['bank_riba_id'] = False
        return result
