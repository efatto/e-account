
from odoo import models


class AccountFiscalPosition(models.Model):
    _name = "account.fiscal.position"
    _inherit = ["account.fiscal.position", "mail.thread"]
