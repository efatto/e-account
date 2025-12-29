from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    trial_balance_exclude = fields.Boolean()
