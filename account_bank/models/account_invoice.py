# -*- coding: utf-8 -*-

from odoo import models, fields, api


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

    bank_riba_id = fields.Many2one(
        'res.bank', 'Bank for ri.ba.',
        readonly=True, states={'draft': [('readonly', False)]})
    actual_bank_riba_id = fields.Many2one(
        'res.bank', compute=_get_actual_bank_riba_id,
        search=_search_actual_bank_riba_id,
        string='Bank for ri.ba.')

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id_bank(self):
        company_id = self.company_id.id
        p = self.partner_id if not company_id else self.partner_id.\
            with_context(force_company=company_id)
        if p.bank_riba_id:
            self.bank_riba_id = p.bank_riba_id
        else:
            self.bank_riba_id = False
        if p.company_bank_id:
            self.partner_bank_id = p.company_bank_id
        else:
            self.partner_bank_id = False

