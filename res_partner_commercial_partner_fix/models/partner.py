# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('partner_id')
    def _get_commercial_partner_id(self):
        for invoice in self:
            current_partner = invoice.partner_id
            while not current_partner.is_company and current_partner.parent_id:
                current_partner = current_partner.parent_id
            invoice.commercial_partner_id = current_partner

    commercial_partner_id = fields.Many2one(
        'res.partner', string='Commercial Entity',
        compute='_get_commercial_partner_id',
        related=False,
        store=True, readonly=True,
        help="The commercial entity that will be used on Journal "
             "Entries for this invoice")
