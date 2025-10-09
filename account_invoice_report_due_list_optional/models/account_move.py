from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("invoice_payment_term_id")
    def _compute_multi_due(self):
        for record in self:
            record.multi_due = (
                record.company_id.due_list_visibility
                or len(record.invoice_payment_term_id.line_ids) > 1
            )
