
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    price_total = fields.Float(
        string="Price Total", compute='_compute_price_total', store=True)

    @api.multi
    @api.depends('price_unit')
    def _compute_price_total(self):
        for move in self:
            move.price_total = move.quantity_done * move.price_unit
