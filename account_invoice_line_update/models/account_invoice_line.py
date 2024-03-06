from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

