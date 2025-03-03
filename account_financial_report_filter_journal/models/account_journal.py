# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError

from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    trial_balance_exclude = fields.Boolean()

    @api.constrains("active")
    def _check_journal_moves(self):
        for journal in self:
            if not journal.active and self.env["account.move"].search([
                ("journal_id", "=", journal.id),
            ]):
                raise ValidationError(
                    _("This journal contains moves and cannot be archived!"))
