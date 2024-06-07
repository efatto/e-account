from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    pec_destinatario = fields.Char(
        "Addressee PEC",
    )
    fiscalcode = fields.Char("Fiscal Code", size=16, help="Italian Fiscal Code")
    codice_destinatario = fields.Char(
        "Addressee Code",
    )
    pa_partner_code = fields.Char("PA Code for Partner", size=20)
    electronic_invoice_subjected = fields.Boolean("Enable electronic invoicing")
    electronic_invoice_obliged_subject = fields.Boolean("Obliged Subject")
