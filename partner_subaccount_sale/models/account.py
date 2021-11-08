# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def onchange_partner_id(self, move_id, partner_id, account_id, debit,
                            credit, date, journal):
        res = super(AccountMoveLine, self).onchange_partner_id(
            move_id, partner_id, account_id, debit, credit, date, journal)
        if not partner_id:
            return res
        partner = self.env['res.partner'].browse(partner_id)
        if partner.property_account_receivable.type == 'view' and \
                partner.customer:
            partner.with_context(create_partner=True).write({'customer': True})
        if partner.property_account_payable.type == 'view' and \
                partner.supplier:
            partner.with_context(create_partner=True).write({'supplier': True})
        if partner.customer:
            res['value'].update(
                {'account_id': partner.property_account_receivable.id})
        elif partner.supplier:
            res['value'].update(
                {'account_id': partner.property_account_payable.id})
        return res
