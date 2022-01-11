# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountVatPeriodEndStatement(models.Model):
    _inherit = "account.vat.period.end.statement"
    _order = 'date desc'
