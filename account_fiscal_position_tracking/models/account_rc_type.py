from odoo import models


class AccountRcType(models.Model):
    _name = "account.rc.type"
    _inherit = ["account.rc.type", "mail.thread"]
