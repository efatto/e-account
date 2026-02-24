from odoo import api, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    @api.model
    def _select(self):
        res = super()._select()
        # Override original select to replace line.balance with line.price_subtotal
        res = res.replace(
            "line.balance",
            "line.price_subtotal "
            "* (CASE WHEN move.move_type IN ("
            "'in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)",
        )
        return res

    @api.model
    def _from(self):
        from_str = super()._from()
        from_str = (
            "%s LEFT JOIN account_move_line_account_tax_rel aml_atr "
            "ON line.id = aml_atr.account_move_line_id "
        ) % from_str
        return from_str

    @api.model
    def _where(self):
        # TODO check if there are invoice lines without tax
        # get even the move lines with a tax set - required - previously grouped by
        # flag "group by account" in account journal - until v. 12.0 - removing filter
        # on exclude_from_invoice_tab
        where_str = super()._where()
        where_str = where_str.replace(
            "AND NOT line.exclude_from_invoice_tab",
            "AND aml_atr.account_tax_id IS NOT NULL",
        )
        return where_str
