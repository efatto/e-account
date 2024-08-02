
from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    export_invoice_reduced_price = fields.Boolean(
        related="partner_id.export_invoice_reduced_price",
        readonly=False,
    )
