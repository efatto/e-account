
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    export_invoice_reduced_price = fields.Boolean(
        string="Export e-invoice with reduced price")


class AccountConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    export_invoice_reduced_price = fields.Boolean(
        related="company_id.export_invoice_reduced_price",
        string="Export e-invoice with reduced price",
        readonly=False)
