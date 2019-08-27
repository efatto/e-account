# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato (https://efatto.it)

from odoo import models, fields, api


class ResBank(models.Model):
    _inherit = "res.bank"

    init_line_to_exclude = fields.Integer(
        'Initial lines to exclude', help='All initial rows to be excluded, '
                                         'including headers.')
    end_line_to_exclude = fields.Integer(
        'End lines to exclude', help='All last rows to be excluded.')
    column_header = fields.Char(
        'Column header', help='List of column headers separated by ;. '
        'Example: date;;label;amount; for a csv with this columns: '
        'Date <omitted> Description Amount <omitted>')
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
    date_format = fields.Char(
        'Date format', help='In EU usually can be set as "%d/%m/%Y".')
    debit_column_pos = fields.Integer(
        'Debit column position', help='Optional if values are splitted in '
                                      'debit and credit.')
    credit_column_pos = fields.Integer(
        'Credit column position', help='Optional if values are splitted in '
                                       'debit and credit.')
    abi_reason_column_pos = fields.Integer(
        'ABI reason position', help='Optional if there is ABI reason column,'
                                    'this will be imported in ref column.')


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    bank_init_line_to_exclude = fields.Integer(
        'Initial lines to exclude', help='All initial rows to be excluded, '
                                         'including headers.')
    bank_end_line_to_exclude = fields.Integer(
        'End lines to exclude', help='All last rows to be excluded.')
    bank_column_header = fields.Char(
        'Column header', help='List of column headers separated by ;. '
        'Example: date;;label;amount; for a csv with this columns: '
        'Date <omitted> Description Amount <omitted>')
    bank_separator = fields.Selection([
        (',', "Comma"),
        (';', "Semicolon"),
        ('\t', "Tab"),
        (' ', "Space")
    ], string="Separator")
    bank_float_thousand_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Thousand separator")
    bank_float_decimal_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Decimal separator")
    bank_date_format = fields.Char(
        'Date format', help='In EU usually can be set as "%d/%m/%Y".')
    bank_debit_column_pos = fields.Integer(
        'Debit column position', help='Optional if values are splitted in '
                                      'debit and credit.')
    bank_credit_column_pos = fields.Integer(
        'Credit column position', help='Optional if values are splitted in '
                                       'debit and credit.')
    bank_abi_reason_column_pos = fields.Integer(
        'ABI reason position', help='Optional if there is ABI reason column,'
                                    'this will be imported in ref column.')

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id:
            self.bank_init_line_to_exclude = self.bank_id.init_line_to_exclude
            self.bank_end_line_to_exclude = self.bank_id.end_line_to_exclude
            self.bank_column_header = self.bank_id.column_header
            self.bank_separator = self.bank_id.separator
            self.bank_date_format = self.bank_id.date_format
            self.bank_float_thousand_separator = \
                self.bank_id.float_thousand_separator
            self.bank_float_decimal_separator = \
                self.bank_id.float_decimal_separator
            self.bank_debit_column_pos = self.bank_id.debit_column_pos
            self.bank_credit_column_pos = self.bank_id.credit_column_pos
            self.bank_abi_reason_column_pos = \
                self.bank_id.abi_reason_column_pos
