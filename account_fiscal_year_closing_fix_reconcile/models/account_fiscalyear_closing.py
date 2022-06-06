# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountFiscalyearClosing(models.Model):
    _inherit = "account.fiscalyear.closing"

    @api.multi
    def _moves_remove(self):
        for closing in self:
            closing.mapped('move_ids.line_ids').remove_move_reconcile()
            closing.move_ids.button_cancel()
            closing.move_ids.unlink()
        return True
