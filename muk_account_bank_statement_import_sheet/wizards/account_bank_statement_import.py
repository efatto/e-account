# -*- coding: utf-8 -*-
#    Copyright (C) 2018 MuK IT GmbH

import os
import base64
import logging

from odoo import api, models, fields
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    bank_init_line_to_exclude = fields.Integer('Initial lines to exclude')
    bank_end_line_to_exclude = fields.Integer('End lines to exclude')
    bank_column_header = fields.Char(
        'Column header', help='List of columns separated by "," or ";"')
    bank_separator = fields.Selection([
        (',', "Comma"),
        (';', "Semicolon"),
        ('\t', "Tab"),
        (' ', "Space")
    ], string="Separator")

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
            if self._context['active_model'] == 'account.journal':
                bank_account = self.env['account.journal'].browse(
                    self._context['journal_id']).bank_account_id
                if bank_account:
                    bank_init_line_to_exclude = bank_account.bank_init_line_to_exclude
                    bank_end_line_to_exclude = bank_account.bank_end_line_to_exclude
                    bank_column_header = bank_account.bank_column_header
                    bank_separator = bank_account.bank_separator
            import_wizard = self.env[
                'account.bank.statement.import.ex.wizard'].create({
                    'res_model': "account.bank.statement.line",
                    'file_name': self.filename,
                    'file': base64.b64decode(self.data_file),
                    'bank_init_line_to_exclude': bank_init_line_to_exclude,
                    'bank_end_line_to_exclude': bank_end_line_to_exclude,
                    'bank_column_header': bank_column_header,
                    'bank_separator': bank_separator,
            })
            ctx = dict(self.env.context)
            ctx['wizard_id'] = import_wizard.id
            ctx['bank_init_line_to_exclude'] = bank_init_line_to_exclude
            ctx['bank_end_line_to_exclude'] = bank_end_line_to_exclude
            ctx['bank_column_header'] = bank_column_header
            ctx['bank_separator'] = bank_separator
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
