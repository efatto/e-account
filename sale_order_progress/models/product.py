from odoo import api, fields, models,  _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_downpayment = fields.Boolean()
