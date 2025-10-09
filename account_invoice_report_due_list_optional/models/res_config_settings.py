from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    due_list_visibility = fields.Boolean(
        help="Make due list visible even with only one date due",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    due_list_visibility = fields.Boolean(
        related="company_id.due_list_visibility",
        help="Make due list visible even with only one date due",
        readonly=False,
    )
