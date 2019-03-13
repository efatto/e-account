# -*- coding: utf-8 -*-
# Copyright 2018 MuK IT GmbH
# Copyright 2019 Sergio Corato (https://efatto.it)

import os
import base64
import logging

from odoo import api, models, fields
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)


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
            values = {
                'res_model': "account.bank.statement.line",
                'file_name': self.filename,
                'file': base64.b64decode(self.data_file),
            }
            if self._context['active_model'] == 'account.journal':
                bank_account = self.env['account.journal'].browse(
                    self._context['journal_id']).bank_account_id
                if bank_account:
                    values.update({
                        'bank_init_line_to_exclude': bank_account.
                        bank_init_line_to_exclude,
                        'bank_end_line_to_exclude': bank_account.
                        bank_end_line_to_exclude,
                        'bank_column_header': bank_account.bank_column_header,
                        'separator': bank_account.bank_separator,
                        'date_format': bank_account.bank_date_format,
                        'float_thousand_separator': bank_account.
                        bank_float_thousand_separator,
                        'float_decimal_separator': bank_account.
                        bank_float_decimal_separator,
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
