# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    carrier_tracking_ref = fields.Char(string="Tracking Reference", copy=False)
    dimension = fields.Char()
