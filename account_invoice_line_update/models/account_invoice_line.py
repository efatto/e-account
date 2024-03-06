from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"
