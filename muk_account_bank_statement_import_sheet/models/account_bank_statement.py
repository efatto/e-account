# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResBank(models.Model):
    _inherit = "res.bank"

    init_line_to_exclude = fields.Integer('Initial lines to exclude')
    end_line_to_exclude = fields.Integer('End lines to exclude')
    column_header = fields.Char(
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


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    bank_init_line_to_exclude = fields.Integer('Initial lines to exclude')
    bank_end_line_to_exclude = fields.Integer('End lines to exclude')
    bank_column_header = fields.Char(
        'Column header', help='List of column headers separated by "," '
                              'and with this format: '
                              'column_field:column_name:column_type'
                              'Where column_field is the db field, '
                              'column_name is the csv field '
                              'and column type is the db type.')
    bank_separator = fields.Selection([
        (',', "Comma"),
        (';', "Semicolon"),
        ('\t', "Tab"),
        (' ', "Space")
    ], string="Separator")

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            self.bank_init_line_to_exclude = self.bank_id.init_line_to_exclude
            self.bank_end_line_to_exclude = self.bank_id.end_line_to_exclude
            self.bank_column_header = self.bank_id.column_header
            self.bank_separator = self.bank_id.separator


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    def default_get(self, vals):
        bank = self.env["account.bank.statement"].browse(
            vals.get('statement_id'))
        if bank.bank_init_lines_to_exclude:
            pass
        if bank.last_lines_to_exclude:
            pass
