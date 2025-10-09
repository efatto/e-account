from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    e_invoice_received_date = fields.Datetime(string="E-Bill Received Datetime")
