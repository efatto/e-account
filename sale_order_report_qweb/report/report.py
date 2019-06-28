# -*- coding: utf-8 -*-

from openerp import api, models, fields


class SaleOrderReportQweb(models.AbstractModel):
    _name = 'report.sale_order_report_qweb.sale_order_qweb'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'sale_order_report_qweb.sale_order_qweb')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'company': False,
            'docs': self.env[report.model].browse(self._ids),
            'address_invoice_id': self._get_invoice_address(
                self.env[report.model].browse(self._ids)
            ),
        }
        return report_obj.render(
            'sale_order_report_qweb.sale_order_qweb',
            docargs)

    def _get_invoice_address(self, objects):
        for sale_order in objects:
            res = sale_order.partner_id
            for address in sale_order.partner_id.child_ids:
                if address.type == 'invoice':
                    res = address
            return res
