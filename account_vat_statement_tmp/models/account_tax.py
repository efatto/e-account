# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    @api.depends('tax_code_id')
    def _get_vat_statement_account_id(self):
        for tax in self:
            if tax.tax_code_id.vat_statement_account_id:
                tax.vat_statement_account_id = tax.tax_code_id.\
                    vat_statement_account_id
            else:
                tax._get_vat_statement_account_tax_code_id(
                    tax, tax.tax_code_id.parent_id)

    def _get_vat_statement_account_tax_code_id(self, tax, tax_code):
        if tax_code.vat_statement_account_id:
            tax.vat_statement_account_id = tax_code.\
                vat_statement_account_id
        else:
            if tax_code.parent_id:
                tax._get_vat_statement_account_tax_code_id(
                    tax, tax_code.parent_id)

    vat_statement_account_id = fields.Many2one(
        'account.account', compute=_get_vat_statement_account_id,
        string="Account used for VAT statement",
        store=True,
    )
