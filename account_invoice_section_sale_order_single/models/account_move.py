from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_ordered_invoice_lines(self):
        """Sort invoice lines according to the section ordering"""
        invoice_section_grouping = self.company_id.invoice_section_grouping
        if invoice_section_grouping == "sale_order":
            return self.invoice_line_ids.sorted(
                key=lambda r: (
                    f"{r.mapped('sale_line_ids.order_id.id')}"
                    f"{r.mapped('sale_line_ids.sequence')}"
                    f"{r.mapped('sale_line_ids.id')}")
            )
        return super()._get_ordered_invoice_lines()
