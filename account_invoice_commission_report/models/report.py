# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models, exceptions, fields
from datetime import datetime


class AccountReportQweb(models.AbstractModel):
    _name = 'report.account_invoice_commission_report.report_account_invoice'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'account_invoice_commission_report.report_account_invoice')
        invoice_ids = self.env['account.invoice'].browse(self._ids)
        agents = invoice_ids.mapped(
            'partner_id.agents')
        if len(agents) != 1:
            invoice_multi_agent_ids = invoice_ids.filtered(
                lambda x: len(x.partner_id.agents) > 1)
            if invoice_multi_agent_ids:
                raise exceptions.ValidationError(
                    'Invoice %s have more than 1 agent or partner!' %
                    invoice_multi_agent_ids.mapped('number'))
            else:
                raise exceptions.ValidationError(
                    'Invoice must be filtered by only 1 customer and the customer must '
                    'have only 1 agent to print commission report.')
        from_date = min(invoice_ids.mapped('date_invoice'))
        to_date = max(invoice_ids.mapped('date_invoice'))
        month = year = False
        if fields.Date.from_string(from_date).month == \
                fields.Date.from_string(to_date).month:
            month = datetime.strftime(fields.Date.from_string(
                from_date), '%B').upper()
            year = datetime.strftime(fields.Date.from_string(from_date), '%Y')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'company': False,
            'docs': self.env[report.model].browse(self._ids),
            'month': month,
            'year': year,
            'agent': agents[0].name.upper(),
        }
        return report_obj.render(
            'account_invoice_commission_report.report_account_invoice',
            docargs)
