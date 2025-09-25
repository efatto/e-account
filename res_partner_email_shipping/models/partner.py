from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    email_shipping = fields.Char(
        string="Email Shipping",
        help="Email address that can be used in email shipping templates",
    )
    email_shipping_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Shipping Email Template",
        domain=[("model_id", "=", "account.move")],
    )
