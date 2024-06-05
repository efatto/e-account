from odoo import fields, models


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    is_fatturapa_pec = fields.Boolean("E-invoice PEC server")
