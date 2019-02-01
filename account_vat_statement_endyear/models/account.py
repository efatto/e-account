# -*- coding: utf-8 -*-

from odoo import models, fields
import openerp.addons.decimal_precision as dp


class AccountVatPeriodEndStatement(models.Model):
    _inherit = "account.vat.period.end.statement"

    endyear_statement = fields.Boolean('End of year statement')

    def _set_debit_lines(self, debit_tax, debit_line_ids, statement):
        total = 0.0
        total_base = 0.0
        for period in statement.date_range_ids:
            totals = debit_tax._compute_totals_tax({
                'from_date': period.date_start,
                'to_date': period.date_end,
                'registry_type': 'customer',
            })
            total += totals[3]  # position 3 is deductible part
            total_base += totals[1]  # position 1 is base amount
        debit_line_ids.append({
            'account_id': debit_tax.vat_statement_account_id.id,
            'tax_id': debit_tax.id,
            'amount': total,
            'amount_base': total_base,
        })

    def _set_credit_lines(self, credit_tax, credit_line_ids, statement):
        total = 0.0
        total_base = 0.0
        for period in statement.date_range_ids:
            totals = credit_tax._compute_totals_tax({
                'from_date': period.date_start,
                'to_date': period.date_end,
                'registry_type': 'supplier',
            })
            total += totals[3]  # position 3 is deductible part
            total_base += totals[1]  # position 1 is base amount
        credit_line_ids.append({
            'account_id': credit_tax.vat_statement_account_id.id,
            'tax_id': credit_tax.id,
            'amount': total,
            'amount_base': total_base,
        })


class StatementDebitAccountLine(models.Model):
    _inherit = 'statement.debit.account.line'

    amount_base = fields.Float(
        'Amount base', digits=dp.get_precision('Account')
    )


class StatementCreditAccountLine(models.Model):
    _inherit = 'statement.credit.account.line'

    amount_base = fields.Float(
            'Amount base', digits=dp.get_precision('Account')
    )
