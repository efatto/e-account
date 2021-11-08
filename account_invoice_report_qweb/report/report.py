# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountInvoiceReportQweb(models.AbstractModel):
    _name = 'report.account_invoice_report_qweb.account_invoice_qweb'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'account_invoice_report_qweb.account_invoice_qweb')
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
            'account_invoice_report_qweb.account_invoice_qweb',
            docargs)

    def _get_invoice_address(self, objects):
        for account_invoice in objects:
            res = account_invoice.partner_id
            for address in account_invoice.partner_id.child_ids:
                if address.type == 'invoice':
                    res = address
            return res

    def _get_bank_riba(self, objects):
        for account_invoice in objects:
            has_bank = bank = False
            if account_invoice.payment_term:
                if account_invoice.payment_term.line_ids:
                    for pt_line in account_invoice.payment_term.line_ids:
                        if pt_line.type == 'RB':
                            has_bank = True
                            break
                if account_invoice.payment_term.type == 'RB':
                    has_bank = True
            if has_bank:
                if account_invoice.partner_id.bank_riba_id:
                    bank = account_invoice.partner_id.bank_riba_id
            return bank if bank else []

    def _get_bank(self, objects):
        for account_invoice in objects:
            company_bank_ids = self.env['res.partner.bank'].search(
                [('company_id', '=', account_invoice.company_id.id)],
                order='sequence', limit=1)
            has_bank = bank = False
            if account_invoice.payment_term:
                if account_invoice.payment_term.line_ids:
                    for pt_line in account_invoice.payment_term.line_ids:
                        if pt_line.type != 'RB' or not pt_line.type:
                            has_bank = True
                            break
                elif account_invoice.payment_term.type != 'RB' \
                        or not account_invoice.payment_term.type:
                    has_bank = True
            if has_bank or not account_invoice.payment_term:
                if account_invoice.partner_id.company_bank_id:
                    bank = account_invoice.partner_id.company_bank_id
                elif account_invoice.partner_id.bank_ids:
                    bank = account_invoice.partner_id.bank_ids[0]
            if not bank and account_invoice.company_id.bank_ids and not \
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
