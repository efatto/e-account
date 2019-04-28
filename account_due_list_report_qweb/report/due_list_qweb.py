# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class DueListReportQweb(models.AbstractModel):
    _name = 'report.account_due_list_report_qweb.duelist_qweb'

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['account.move.line'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.env['account.move.line'],
            'data': data,
            'docs': docs,
            'get_group': self._get_group(docs),
        }
        return self.env['report'].render(
            'account_due_list_report_qweb.duelist_qweb', docargs)

    def _get_group(self, objects):
        res = {}
        for line in objects:
            if not line.date_maturity:
                date = fields.Date.today()
            else:
                date = line.date_maturity
            date_maturity = datetime.strptime(
                date, DEFAULT_SERVER_DATE_FORMAT
            ).strftime('%d/%m/%Y')

            if date_maturity not in res:
                res.update({date_maturity: [line]})
            else:
                res[date_maturity] = res[date_maturity] + [line]
        dates = sorted([datetime.strptime(ts, "%d/%m/%Y") for ts in res])
        dates_sorted = [datetime.strftime(ts, "%d/%m/%Y") for ts in dates]
        return res, dates_sorted
