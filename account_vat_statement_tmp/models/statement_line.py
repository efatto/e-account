# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StatementDebitAccountLine(models.Model):
    _inherit = 'statement.debit.account.line'

    @api.multi
    @api.depends('tax_code_id')
    def _get_statement_debit_tax_id(self):
        tax_model = self.env['account.tax']
        for line in self:
            tax_code = line.tax_code_id
            tax_id = tax_model.search([
                '|',
                ('tax_code_id', '=', tax_code.id),
                ('base_code_id', '=', tax_code.id)],
                order='sequence asc', limit=1)
            if tax_id:
                line.tax_id = tax_id[0].id
            else:
                if line.tax_code_id.parent_id:
                    tax_code = line.tax_code_id.parent_id
                tax_id = tax_model.search([
                    '|',
                    ('tax_code_id', '=', tax_code.id),
                    ('base_code_id', '=', tax_code.id)],
                    order='sequence asc', limit=1)
                if tax_id:
                    line.tax_id = tax_id[0].id

    tax_id = fields.Many2one(
        'account.tax', compute=_get_statement_debit_tax_id,
        string="Tax",
        store=True,
    )


class StatementCreditAccountLine(models.Model):
    _inherit = 'statement.credit.account.line'

    @api.multi
    @api.depends('tax_code_id')
    def _get_statement_credit_tax_id(self):
        tax_model = self.env['account.tax']
        for line in self:
            tax_code = line.tax_code_id
            tax_id = tax_model.search([
                '|',
                ('tax_code_id', '=', tax_code.id),
                ('base_code_id', '=', tax_code.id)],
                order='sequence asc', limit=1)
            if tax_id:
                line.tax_id = tax_id[0].id
            else:
                if line.tax_code_id.parent_id:
                    tax_code = line.tax_code_id.parent_id
                tax_id = tax_model.search([
                    '|',
                    ('tax_code_id', '=', tax_code.id),
                    ('base_code_id', '=', tax_code.id)],
                    order='sequence asc', limit=1)
                if tax_id:
                    line.tax_id = tax_id[0].id

    tax_id = fields.Many2one(
        'account.tax', compute=_get_statement_credit_tax_id,
        string="Tax",
        store=True,
    )
