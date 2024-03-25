from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("partner_id")
    def _partner_id_onchange(self):
        if self.partner_id:
            if self.partner_id.customer_rank > self.partner_id.supplier_rank:
                self.account_id = self.partner_id.property_account_receivable_id
            else:
                self.account_id = self.partner_id.property_account_payable_id

    name = fields.Text("Name", required=True)
    date_from = fields.Date(compute=lambda *a, **k: {}, string="Date from")
    date_to = fields.Date(compute=lambda *a, **k: {}, string="Date to")
