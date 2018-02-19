# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class DueListReportQweb(models.AbstractModel):
    _name = 'report.account_due_list_report_qweb.duelist_qweb'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'account_due_list_report_qweb.duelist_qweb')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'company': False,
            'docs': self.env[report.model].browse(self._ids),
            'get_group': self._get_group(
                self.env[report.model].browse(self._ids)
            ),
        }
        return report_obj.render(
            'account_due_list_report_qweb.duelist_qweb',
            docargs)

    def _get_group(self, objects):
        res = {}
        for line in objects:
            date_maturity = datetime.strptime(
                line.date_maturity, DEFAULT_SERVER_DATE_FORMAT
            ).strftime('%d/%m/%Y')
            if not date_maturity in res:
                res.update({date_maturity: [line]})
            else:
                res[date_maturity] = res[date_maturity] + [line]
        return res
