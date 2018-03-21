# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, _, api
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import xlwt
from openerp.http import request
import re


class InvoiceStatement(models.Model):
    _inherit = "invoice.statement"

    def get_date_start_stop(self):
        date_start = False
        date_stop = False
        for period in self.period_ids:
            if not date_start:
                date_start = period.date_start
            else:
                if period.date_start < date_start:
                    date_start = period.date_start
            if not date_stop:
                date_stop = period.date_stop
            else:
                if period.date_stop > date_stop:
                    date_stop = period.date_stop
        date_start = datetime.datetime.strptime(date_start,
                                                DEFAULT_SERVER_DATE_FORMAT)
        date_stop = datetime.datetime.strptime(date_stop,
                                               DEFAULT_SERVER_DATE_FORMAT)
        return date_start, date_stop

    @api.multi
    def btn_export(self):
        wb = xlwt.Workbook(encoding="UTF-8")
        ws = wb.add_sheet('sheet_name')

        statement_id = self
        date_start, date_stop = self.get_date_start_stop()
        DTR_invoice_ids = self.env['account.invoice'].search([
            ('registration_date', '>=', date_start),
            ('registration_date', '<=', date_stop),
            ('type', 'in', ['in_invoice', 'in_refund'],),
            ('state', 'in', ['open', 'paid']),
            '|', ('fiscal_document_type_id.code', '!=', 'NONE'),
            ('fiscal_document_type_id', '=', False),
        ])
        summary_invoice_ids = DTR_invoice_ids.filtered(
            lambda x: x.fiscal_document_type_id.code == 'TD12')
        summary_partner_ids = summary_invoice_ids.mapped('partner_id')
        DTE_invoice_ids = self.env['account.invoice'].search([
            ('registration_date', '>=', date_start),
            ('registration_date', '<=', date_stop),
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('state', 'in', ['open', 'paid']),
            '|', ('fiscal_document_type_id.code', '!=', 'NONE'),
            ('fiscal_document_type_id', '=', False),
        ])
        auto_invoice_ids = DTR_invoice_ids.filtered('auto_invoice_id')
        DTE_invoice_ids -= auto_invoice_ids

        if statement_id.type == 'DTR':
            invoice_ids = DTR_invoice_ids
        elif statement_id.type == 'DTE':
            invoice_ids = DTE_invoice_ids

        partner_ids = invoice_ids.mapped('partner_id')
        if partner_ids:
            row = 0
            ws.write(0, 0, 'Name')
            ws.write(0, 1, 'Id')
            ws.write(0, 2, 'Errors')
            ws.write(0, 3, 'Invoice Number')
            ws.write(0, 4, 'Invoices Errors')
            for partner_id in partner_ids:
                errors = []
                if partner_id not in summary_partner_ids:
                    if not partner_id.street:
                        errors.append(
                            'Missing partner street')
                    if not partner_id.city:
                        errors.append(
                            'Missing partner city')
                    if not partner_id.country_id:
                        errors.append(
                            'Missing partner country')
                    if not partner_id.vat and not partner_id.fiscalcode:
                        errors.append(
                            'Missing partner vat or fiscalcode')
                if errors:
                    row += 1
                    ws.write(row, 0, partner_id.name)
                    ws.write(row, 1, partner_id.id)
                    ws.write(row, 2, str(errors))

                for invoice in invoice_ids.filtered(
                        lambda x: x.partner_id == partner_id):
                    invoices_errors = []
                    if not invoice.date_invoice:
                        invoices_errors.append(
                            'Missing date invoice')
                    if statement_id.type == 'DTR':
                        if not invoice.supplier_invoice_number:
                            invoices_errors.append(
                                'Missing supplier invoice number')
                    elif statement_id.type == 'DTE':
                        if not invoice.number:
                            invoices_errors.append(
                                'Missing customer invoice number')
                    if not invoice.registration_date:
                        invoices_errors.append(
                            'Missing invoice registration date')
                    if invoices_errors:
                        row += 1
                        ws.write(row, 0, partner_id.name)
                        ws.write(row, 1, partner_id.id)
                        ws.write(row, 3, invoice.number)
                        ws.write(row, 4, str(invoices_errors))
                    if invoice.tax_line:
                        for invoice_tax in invoice.tax_line:
                            if invoice_tax.tax_code_id and not \
                                    invoice_tax.tax_code_id.\
                                    exclude_from_registries:
                                tax_id = invoice_tax.tax_code_id.tax_ids[0]
                                # if tax_id is a child of other tax, use it for aliquota
                                if tax_id.parent_id and tax_id.parent_id.child_depend:
                                    tax_id = tax_id.parent_id
                                if tax_id.amount == 0.0:
                                    if not tax_id.kind_id:
                                        row += 1
                                        ws.write(row, 0, partner_id.name)
                                        ws.write(row, 1, partner_id.id)
                                        ws.write(row, 3, invoice.number)
                                        ws.write(row, 4, 'Tax %s without kind'
                                                 % tax_id.description)
                            else:
                                if invoice_tax.base_code_id and not \
                                        invoice_tax.base_code_id. \
                                        exclude_from_registries:
                                    tax_id = invoice_tax.base_code_id.base_tax_ids[0]
                                    if not tax_id.kind_id.code:
                                        row += 1
                                        ws.write(row, 0, partner_id.name)
                                        ws.write(row, 1, partner_id.id)
                                        ws.write(row, 3, invoice.number)
                                        ws.write(row, 4, 'Tax %s without kind'
                                                 % tax_id.name)
                    else:
                        row += 1
                        ws.write(row, 0, partner_id.name)
                        ws.write(row, 1, partner_id.id)
                        ws.write(row, 3, invoice.number)
                        ws.write(row, 4, 'Missing Tax in invoice')

        request.session['wb'] = wb
        return {
            'type': 'ir.actions.act_url',
            'url': '/l10n_it_account_invoice_statement/export_report/'
                   'download_xls_report?model=invoice.statement',
            'target': 'new',
        }
