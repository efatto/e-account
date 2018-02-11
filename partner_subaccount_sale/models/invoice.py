# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.cr_uid_ids_context
    def onchange_partner_id(
            self, cr, uid, ids, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False,
            context=None):
        res = super(AccountInvoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice, payment_term,
            partner_bank_id, company_id, context)
        if not partner_id:
            return res
        partner = self.pool['res.partner'].browse(cr, uid, partner_id, context)
        if partner.property_account_receivable.type == 'view' and \
                partner.customer:
            ctx = context.copy()
            ctx['create_partner'] = True
            self.pool['res.partner'].write(
                cr, uid, [partner_id], {'customer': True}, context=ctx)
            if type in ['out_invoice', 'out_refund']:
                res['value'].update(
                    {'account_id': partner.property_account_receivable.id})
        if partner.property_account_payable.type == 'view' and \
                partner.supplier:
            ctx = context.copy()
            ctx['create_partner'] = True
            self.pool['res.partner'].write(
                cr, uid, [partner_id], {'supplier': True}, context=ctx)
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
