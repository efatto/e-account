
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    export_invoice_reduced_price = fields.Boolean(
        "Export e-invoice with net price")
