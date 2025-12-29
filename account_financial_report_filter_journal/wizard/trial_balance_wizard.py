from odoo import api, fields, models


class TrialBalanceReportWizard(models.TransientModel):
    _inherit = "trial.balance.report.wizard"

    @api.model
    def _get_journal(self):
        journal_obj = self.env["account.journal"]
        journal_ids = journal_obj.search(
            [
                ("trial_balance_exclude", "=", False),
            ]
        )
        return journal_ids

    journal_ids = fields.Many2many(default=_get_journal)
