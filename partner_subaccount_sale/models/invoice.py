# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def onchange_partner_id(self, type, partner_id):
        res = super(AccountInvoice, self).onchange_partner_id(type, partner_id)
        if not partner_id:
            return res
        partner = self.env['res.partner'].browse(partner_id)
        if partner.property_account_receivable.type == 'view' and \
                partner.customer:
            partner.with_context(create_partner=True).write({'customer': True})
            if type in ['out_invoice', 'out_refund']:
                res['value'].update(
                    {'account_id': partner.property_account_receivable.id})
        if partner.property_account_payable.type == 'view' and \
                partner.supplier:
            partner.with_context(create_partner=True).write({'supplier': True})
            if type in ['in_invoice', 'in_refund']:
                res['value'].update(
                    {'account_id': partner.property_account_payable.id})
        return res

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if not res.partner_id:
            return res
        if res.account_id.type == 'view':
            partner = res.partner_id
            if partner.property_account_receivable.type == 'view' and \
                    partner.customer:
                partner.with_context(create_partner=True).write(
                    {'customer': True})
                if type in ['out_invoice', 'out_refund']:
                    res.update(
                        {'account_id': partner.property_account_receivable.id})
            if partner.property_account_payable.type == 'view' and \
                    partner.supplier:
                partner.with_context(create_partner=True).write(
                    {'supplier': True})
                if type in ['in_invoice', 'in_refund']:
                    res.update(
                        {'account_id': partner.property_account_payable.id})
        return res
