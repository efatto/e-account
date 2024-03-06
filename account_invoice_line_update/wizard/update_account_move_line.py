from odoo import fields, models


class UpdateAccountMoveLineWizard(models.TransientModel):
    _name = "wizard.update.account.move.line"
    _description = "Wizard update account move line"

    account_id = fields.Many2one(comodel_name="account.account", required=True)

    def update_account_move_line(self):
        rec_ids = self.env.context.get("active_ids", False)
        records = self.env[self.env.context["active_model"]].browse(rec_ids)
        for rec in records:
            rec.write(
                {
                    "account_id": self.account_id.id,
                }
            )
