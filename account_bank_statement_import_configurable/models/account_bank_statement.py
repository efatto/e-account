# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato (https://efatto.it)

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
    float_thousand_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Thousand separator")
    float_decimal_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Decimal separator")
    date_format = fields.Char('Date format')


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
    bank_float_thousand_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Thousand separator")
    bank_float_decimal_separator = fields.Selection([
        (',', "Comma"),
        ('.', "Dot"),
    ], string="Decimal separator")
    bank_date_format = fields.Char('Date format')

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
