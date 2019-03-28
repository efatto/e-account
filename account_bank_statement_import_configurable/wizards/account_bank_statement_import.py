# -*- coding: utf-8 -*-
# Copyright 2018 MuK IT GmbH
# Copyright 2019 Sergio Corato (https://efatto.it)

import os
import base64
import csv
import logging
import itertools
import operator

from odoo import api, models, fields
from odoo.tools.mimetypes import guess_mimetype

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

_logger = logging.getLogger(__name__)


class Import(models.TransientModel):
    _inherit = 'base_import.import'

    @api.model
    def _convert_import_data(self, fields, options):
        data, import_fields = super(
            Import, self)._convert_import_data(fields, options)

        if self._context.get('init_line_to_exclude'):
            indices = [index for index, field in enumerate(fields) if
                       field]
            if len(indices) == 1:
                mapper = lambda row: [row[indices[0]]]
            else:
                mapper = operator.itemgetter(*indices)
            rows_to_import = self._read_file(options)
            init_line_to_exclude = self._context['init_line_to_exclude']
            if options.get('headers'):
                init_line_to_exclude -= 1
            rows_to_import = itertools.islice(
                rows_to_import, init_line_to_exclude, None)
            data = [
                list(row) for row in itertools.imap(mapper, rows_to_import)
                if any(row)
            ]

        return data, import_fields


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    @staticmethod
    def _check_csv(data_file, filename):
        return guess_mimetype(data_file) == 'text/csv' or \
             filename and os.path.splitext(filename)[1] == '.csv'

    @staticmethod
    def _check_xls(data_file, filename):
        return guess_mimetype(data_file) == 'application/vnd.ms-excel' or \
             filename and os.path.splitext(filename)[1] == '.xls'

    @staticmethod
    def _check_xlsx(data_file, filename):
        return guess_mimetype(data_file) == \
            'application/vnd.openxmlformats-officedocument.spreadsheetml.' \
            'sheet' or filename and os.path.splitext(filename)[1] == '.xlsx'

    @staticmethod
    def _check_ods(data_file, filename):
        return guess_mimetype(data_file) == \
            'application/vnd.oasis.opendocument.spreadsheet' or \
            filename and os.path.splitext(filename)[1] == '.ods'

    @api.multi
    def import_file(self):
        if self._check_csv(self.data_file, self.filename) or \
            self._check_xls(self.data_file, self.filename) or \
            self._check_xlsx(self.data_file, self.filename) or \
                self._check_ods(self.data_file, self.filename):
            values = {}
            bank_account = False
            if self._context['active_model'] == 'account.journal':
                bank_account = self.env['account.journal'].browse(
                    self._context['journal_id']).bank_account_id
                if bank_account:
                    values.update({
                        'bank_column_header': bank_account.bank_column_header,
                        'separator': bank_account.bank_separator,
                        'date_format': bank_account.bank_date_format,
                        'float_thousand_separator': bank_account.
                        bank_float_thousand_separator,
                        'float_decimal_separator': bank_account.
                        bank_float_decimal_separator,
                    })

            # todo change on-the-fly file csv to drop init-end lines
            # todo move amount in 2nd column of values to the 1st with - sign
            if bank_account and bank_account.bank_debit_column_pos and \
                    bank_account.bank_credit_column_pos:
                abi_reason_column_pos = bank_account.bank_abi_reason_column_pos
                credit_col_pos = bank_account.bank_credit_column_pos
                debit_col_pos = bank_account.bank_debit_column_pos
                first_column = (credit_col_pos < debit_col_pos
                               ) and credit_col_pos or debit_col_pos
                last_column = (credit_col_pos > debit_col_pos
                               ) and credit_col_pos or debit_col_pos
                new_rows = []
                csv_data = base64.b64decode(self.data_file)
                # encoding = self.options.get('encoding', 'utf-8')
                # if encoding != 'utf-8':
                #     # csv module expect utf-8,
                #     # see http://docs.python.org/2/library/csv.html
                #     csv_data = csv_data.decode(encoding).encode('utf-8')
                csv_iterator = csv.reader(
                    StringIO(csv_data),
                    delimiter=str(bank_account.bank_separator))
                rows = 0
                if bank_account.bank_end_line_to_exclude:
                    csv_iterator1 = csv.reader(
                        StringIO(csv_data),
                        delimiter=str(bank_account.bank_separator))
                    rows = len(list(csv_iterator1))
                i = 0
                for row in csv_iterator:
                    i += 1
                    if i == 1:
                        new_rows.append(row)
                        continue
                    if abi_reason_column_pos \
                            and not row[abi_reason_column_pos]:
                        continue
                    if bank_account.bank_end_line_to_exclude and \
                            bank_account.bank_end_line_to_exclude == (
                            rows + 1 - i):
                        break
                    if bank_account.bank_init_line_to_exclude and \
                            bank_account.bank_init_line_to_exclude >= i:
                        continue
                    debit_val = False
                    credit_val = False
                    if row[debit_col_pos].strip() != '':
                        debit_val = float(
                            row[debit_col_pos].strip(
                                ).replace('.', '').replace(',', '.'))
                    if row[credit_col_pos].strip() != '':
                        credit_val = float(
                            row[credit_col_pos].strip(
                                ).replace('.', '').replace(',', '.'))
                    if credit_val:
                        debit_val = credit_val * -1
                    if debit_val:
                        new_row = row[:first_column]
                        new_row.append(str(debit_val).replace('.', ','))
                        new_row += row[last_column+1:]
                        new_rows.append(new_row)

                fp = StringIO()
                writer = csv.writer(fp, quoting=csv.QUOTE_ALL,
                                    delimiter=str(bank_account.bank_separator))
                writer.writerows(new_rows)
                fp.seek(0)
                data = fp.read()
                fp.close()
                self.data_file = base64.b64encode(data)

            values.update({
                'res_model': "account.bank.statement.line",
                'file_name': self.filename,
                'file': base64.b64decode(self.data_file),
            })
            import_wizard = self.env[
                'account.bank.statement.import.ex.wizard'].create(values)
            ctx = dict(self.env.context)
            ctx['wizard_id'] = import_wizard.id
            if bank_account:
                ctx.update({
                    'separator': bank_account.bank_separator,
                    'date_format': bank_account.bank_date_format,
                    'float_thousand_separator': bank_account.
                    bank_float_thousand_separator,
                    'float_decimal_separator': bank_account.
                    bank_float_decimal_separator,
                    'init_line_to_exclude': bank_account.
                    bank_init_line_to_exclude,
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'import_bank_statement',
                'params': {
                    'model': "account.bank.statement.line",
                    'filename': self.filename,
                    'context': ctx,
                }
            }
        else:
            return super(AccountBankStatementImport, self).import_file()
