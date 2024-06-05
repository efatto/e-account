from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fatturapa_fiscal_position_code = fields.Char("Code", size=4)
