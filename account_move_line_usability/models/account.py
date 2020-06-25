# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('credit')
    def _credit_onchange(self):
        if self.credit and self.debit:
            self.debit = 0

    @api.onchange('debit')
    def _debit_onchange(self):
        if self.debit and self.credit:
            self.credit = 0

    name = fields.Text('Name', required=True)
    date_from = fields.Date(
        compute=lambda *a, **k: {},
        string="Date from")
    date_to = fields.Date(
        compute=lambda *a, **k: {},
        string="Date to")

    @api.model
    def default_get(self, fields):
        data = super(AccountMoveLine, self).default_get(fields)
        if data and self._context.get('line_ids', False) and all(
            y[2] for y in self._context['line_ids']
        ):
            debit = credit = 0
            for x in self._context['line_ids']:
                debit += x[2]['debit']
            for x in self._context['line_ids']:
                credit += x[2]['credit']
            balance = credit - debit
            if balance > 0:
                data['debit'] = balance
            elif balance < 0:
                data['credit'] = abs(balance)
        return data
