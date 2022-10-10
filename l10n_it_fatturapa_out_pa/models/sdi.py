from odoo import api, fields, models,  _


class SdiChannel(models.Model):
    _inherit = "sdi.channel"

    is_pa_sign_automatic = fields.Boolean()
