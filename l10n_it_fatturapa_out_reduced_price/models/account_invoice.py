
from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    export_invoice_reduced_price = fields.Boolean()
