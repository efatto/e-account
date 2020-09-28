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
                self.env[report.model].browse(self._ids)),
            'get_bank_riba': self._get_bank_riba(
                self.env[report.model].browse(self._ids)),
            'get_bank': self._get_bank(
                self.env[report.model].browse(self._ids)),
            'check_installed_module': self._check_installed_module,
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

    def _get_bank_riba(self, objects):
        for sale_order in objects:
            has_bank = bank = False
            if sale_order.payment_term:
                if sale_order.payment_term.line_ids:
                    for pt_line in sale_order.payment_term.line_ids:
                        if pt_line.type == 'RB':
                            has_bank = True
                            break
                if sale_order.payment_term.type == 'RB':
                    has_bank = True
            if has_bank:
                if sale_order.partner_id.bank_riba_id:
                    bank = sale_order.partner_id.bank_riba_id
            return bank if bank else []

    def _get_bank(self, objects):
        for sale_order in objects:
            company_bank_ids = self.env['res.partner.bank'].search(
                [('company_id', '=', sale_order.company_id.id)],
                order='sequence', limit=1)
            has_bank = bank = False
            if sale_order.payment_term:
                if sale_order.payment_term.line_ids:
                    for pt_line in sale_order.payment_term.line_ids:
                        if pt_line.type != 'RB' or not pt_line.type:
                            has_bank = True
                            break
                elif sale_order.payment_term.type != 'RB' \
                        or not sale_order.payment_term.type:
                    has_bank = True
            if has_bank or not sale_order.payment_term:
                if sale_order.partner_id.company_bank_id:
                    bank = sale_order.partner_id.company_bank_id
                elif sale_order.partner_id.bank_ids:
                    bank = sale_order.partner_id.bank_ids[0]
            if not bank and sale_order.company_id.bank_ids and not \
                    self.env['ir.config_parameter'].get_param(
                        'report.not.print.default.bank',
                        default=False):
                if company_bank_ids:
                    bank = company_bank_ids[0]
            return bank if bank else []

    def _check_installed_module(self, module):
        res = False
        if self.env['ir.module.module'].search(
                [('name', '=', module), ('state', '=', 'installed')]):
            res = True
        return res