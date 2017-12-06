# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_number(self):
        res = super(AccountInvoice, self).action_number()
        for invoice in self:
            if invoice.type in ('out_invoice', 'out_refund'):
                registration_fy_id = self.env['account.fiscalyear'].find(
                    dt=self.date_invoice)
                last_open_period = self.env['account.period'].search([
                    ('invoicing_closed', '=', False),
                    ('special', '=', False),
                    ('fiscalyear_id', '=', registration_fy_id)
                ], order='date_stop asc', limit=1)
                if invoice.date_invoice > last_open_period.date_stop:
                    raise exceptions.ValidationError(
                        _('Cannot create invoice! The current period of '
                          'invoicing has max date available: %s')
                        % datetime.strptime(
                            last_open_period.date_stop,
                            DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                    )
                elif invoice.registration_date > invoice.date_invoice:
                    invoice.registration_date = invoice.date_invoice
        return res


class AccountPeriod(models.Model):
    _inherit = "account.period"

    invoicing_closed = fields.Boolean()
