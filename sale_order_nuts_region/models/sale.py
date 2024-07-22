from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    nuts3_id = fields.Many2one(
        string="Region",
        related="partner_id.nuts3_id",
        store=True,
    )
