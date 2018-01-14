# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    name = fields.Text('Name', required=True)

    @api.onchange('credit')
    def _credit_onchange(self):
        if self.credit and self.debit:
            self.debit = 0

    @api.onchange('debit')
    def _debit_onchange(self):
        if self.debit and self.credit:
            self.credit = 0

    user_type = fields.Many2one(
            related='account_id.user_type',
            relation='account.account',
            string='Account user type',
            store=False)
    date_from = fields.Date(
        compute=lambda *a, **k: {},
        string="Date from")
    date_to = fields.Date(
        compute=lambda *a, **k: {},
        string="Date to")

    @api.model
    def default_get(self, fields):
        data = super(AccountMoveLine, self).default_get(fields)
        if data:
            if 'partner_id' in data:
                data['partner_id'] = False
            if 'name' in data and self.env['ir.config_parameter'].get_param(
                    'account.move.line.not.copy.name'):
                data['name'] = False
        return data
