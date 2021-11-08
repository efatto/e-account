# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_actual_bank_riba_id(self):
        for inv in self:
            inv.actual_bank_riba_id = inv.bank_riba_id \
                                      or inv.partner_id.bank_riba_id

    @api.model
    def _search_actual_bank_riba_id(self, op, arg):
        if op not in ['=', 'ilike', 'like'] or not arg:
            return [('id', '=', False)]
        if op == '=' and isinstance(arg, (int, long)):
            domain = ['|', ('bank_riba_id', '=', arg),
                      ('partner_id.bank_riba_id', '=', arg)]
        if op in ['ilike', 'like'] and isinstance(arg, str):
            domain = ['|', ('bank_riba_id.name', 'ilike', arg),
                      ('partner_id.bank_riba_id.name', 'ilike', arg)]
        return [('id', 'in', self.search(domain).ids)]

    bank_riba_id = fields.Many2one('res.bank', 'Bank for ri.ba.')
    actual_bank_riba_id = fields.Many2one(
        'res.bank', compute=_get_actual_bank_riba_id,
        search=_search_actual_bank_riba_id,
        string='Bank for ri.ba.')

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
