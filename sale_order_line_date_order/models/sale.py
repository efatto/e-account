from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_order = fields.Datetime(
        related='order_id.date_order'
    )
