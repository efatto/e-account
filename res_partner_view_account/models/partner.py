from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def show_receivable_account(self):
        self.ensure_one()
        account_id = self.property_account_receivable_id.id
        return self.common_show_account(self.ids[0], account_id)

    def show_payable_account(self):
        self.ensure_one()
        account_id = self.property_account_payable_id.id
        return self.common_show_account(self.ids[0], account_id)

    def common_show_account(self, partner_id, account_id):
        action = self.env["ir.actions.act_window"].for_xml_id(
            "account", "action_account_moves_all_tree"
        )
        action["context"] = {
            "search_default_partner_id": [partner_id],
            "default_partner_id": partner_id,
            "search_default_account_id": account_id,
        }
        return action

    def _compute_journal_item_count(self):
        amlo = self.env["account.move.line"]
        for partner in self:
            partner.journal_item_count = amlo.search_count(
                [
                    ("partner_id", "=", partner.id),
                    ("account_id", "=", partner.property_account_receivable_id.id),
                ]
            )
            partner.payable_journal_item_count = amlo.search_count(
                [
                    ("partner_id", "=", partner.id),
                    ("account_id", "=", partner.property_account_payable_id.id),
                ]
            )

    journal_item_count = fields.Integer(
        compute="_compute_journal_item_count", string="Journal Items", readonly=True
    )
    payable_journal_item_count = fields.Integer(
        compute="_compute_journal_item_count",
        string="Payable Journal Items",
        readonly=True,
    )
