# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class VatPeriodEndStatementReport(models.AbstractModel):
    _inherit = 'report.account_vat_period_end_statement.vat_statement'

    def _get_taxes_amounts(
        self, period_id, tax_ids=None, registry_type='customer'
    ):
        res = super()._get_taxes_amounts(
            period_id=period_id, tax_ids=tax_ids, registry_type=registry_type)
        if tax_ids is None:
            tax_ids = []
        date_range = self.env['date.range'].browse(period_id)
        tax_model = self.env['account.tax']

        for tax_id in tax_ids:
            tax = tax_model.browse(tax_id)
            tax_name, base, tax_val, deductible, undeductible = (
                tax._compute_totals_tax({
                    'from_date': date_range.date_start,
                    'to_date': date_range.date_end,
                    'registry_type': registry_type,
                })
            )
            res[tax_name].update(dict(description=tax.description))
        return res
