from odoo import api, models
from odoo.tools import SQL


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    @api.model
    def _from(self) -> SQL:
        return SQL(
            """
                %s
                LEFT JOIN account_move_line_account_tax_rel aml_atr
                ON line.id = aml_atr.account_move_line_id
            """,
            super()._from(),
        )

    @api.model
    def _where(self) -> SQL:
        # get even the move lines of type income or expense - previously grouped by
        # flag "group by account" in account journal - until v. 12.0 - removing filter
        # on exclude_from_invoice_tab
        return SQL(
            super()
            ._where()
            .code.replace(
                "AND NOT line.exclude_from_invoice_tab",
                "AND aml_atr.account_tax_id IS NOT NULL",
            )
        )
