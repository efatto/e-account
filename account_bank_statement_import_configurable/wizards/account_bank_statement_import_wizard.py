# -*- coding: utf-8 -*-
# Copyright (C) 2018 MuK IT GmbH
# Copyright 2019 Sergio Corato (https://efatto.it)

import os
import datetime
import logging
import psycopg2

from odoo import _
from odoo import api, models, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class AccountBankStatementImportExWizard(models.TransientModel):
    _name = "account.bank.statement.import.ex.wizard"
    _inherit = "base_import.import"

    bank_init_line_to_exclude = fields.Integer('Initial lines to exclude')
    bank_end_line_to_exclude = fields.Integer('End lines to exclude')
    bank_column_header = fields.Char(
        'Column header', help='List of column headers separated by "," '
                              'and with this format: '
                              'column_field:column_name:column_type'
                              'Where column_field is the db field, '
                              'column_name is the csv field '
                              'and column type is the db type.')
    separator = fields.Selection([
        (',', "Comma"),
        (';', "Semicolon"),
        ('\t', "Tab"),
        (' ', "Space")
    ], string="Separator")
    float_thousand_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Thousand separator")
    float_decimal_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Decimal separator")
    date_format = fields.Char('Date format')

    @api.multi
    def parse_preview(self, options, count=10):
        if self.date_format:
            options['date_format'] = self.date_format
        return super(AccountBankStatementImportExWizard, self).parse_preview(
            options, count=count)

    def _match_headers(self, rows, fields, options):
        res = super(AccountBankStatementImportExWizard, self)._match_headers(
            rows, fields, options)
        if self.bank_column_header:
            # get column names from bank settings and use for match
            sep = ';'
            if ',' in self.bank_column_header:
                sep = ','
            headers = self.bank_column_header.split(sep)
            res = headers, {
                index: [field['name'] for field in
                        self._match_header(header, fields,
                                           options)] or None
                for index, header in enumerate(headers)
            }
        return res

    def _parse_float(self, value):
        return float(value) if value else 0.0

    def _prepare_statement(self):
        date = datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
        filename = self.file_name and os.path.splitext(self.file_name)[0] or ""
        return self.env['account.bank.statement'].create({
            'journal_id': self._context.get('journal_id', False),
            'name': _("%s - Import %s") % (date, filename),
            'reference': self.file_name})

    def _update_statement(self, data, import_fields, options):
        vals = {}
        date_index = import_fields.index('date') if 'date' in import_fields\
            else False
        balance_index = import_fields.index('balance')\
            if 'balance' in import_fields else False
        statment_index = import_fields.index('statement_id/.id')
        if date_index:
            vals['date'] = data[len(data) - 1][date_index]
        if balance_index:
            self._parse_float_from_data(
                data, balance_index, 'balance', options)
            vals['balance_start'] = self._parse_float(data[0][balance_index])
            vals['balance_end_real'] = self._parse_float(
                data[len(data) - 1][balance_index])
        self.env['account.bank.statement'].browse(
            data[0][statment_index]).write(vals)

    @api.model
    def _convert_import_data(self, fields, options):
        data, import_fields = super(
            AccountBankStatementImportExWizard, self)._convert_import_data(
                fields, options)
        bank_statement = self._prepare_statement()
        import_fields.append('sequence')
        import_fields.append('statement_id/.id')
        for index, row in enumerate(data):
            row.append(index)
            row.append(bank_statement.id)
        return data, import_fields

    @api.multi
    def _parse_import_data(self, data, import_fields, options):
        parsed_data = super(
            AccountBankStatementImportExWizard, self)._parse_import_data(
                data, import_fields, options)
        self._update_statement(parsed_data, import_fields, options)
        balance_index = import_fields.index('balance') \
            if 'balance' in import_fields else False
        amount_index = import_fields.index('amount') \
            if 'amount' in import_fields else False
        bank_data = []
        for row in parsed_data:
            if row[amount_index]:
                if balance_index:
                    del row[balance_index]
                bank_data.append(row)
        if balance_index:
            import_fields.remove('balance')
        return bank_data

    @api.multi
    def do(self, fields, options, dryrun=False):
        self._cr.execute('SAVEPOINT import_bank_statement')
        res = super(AccountBankStatementImportExWizard, self).do(
            fields, options, dryrun)
        try:
            if dryrun:
                self._cr.execute('ROLLBACK TO SAVEPOINT import_bank_statement')
            else:
                self._cr.execute('RELEASE SAVEPOINT import_bank_statement')
        except psycopg2.InternalError as e:
            _logger.debug(e)
        return res
