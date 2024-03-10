from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    exclude_from_discount = fields.Boolean(
        string="Exclude from discount"
    )
