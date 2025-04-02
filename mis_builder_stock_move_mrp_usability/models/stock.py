
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    bom_price_total = fields.Float(
        string="Price Total from BOM", compute='_compute_bom_price_total', store=True)

    @api.multi
    @api.depends('bom_line_price_unit', 'price_unit', 'quantity_done')
    def _compute_bom_price_total(self):
        for move in self:
            move.bom_price_total = move.quantity_done * (
                - move.bom_line_price_unit or move.price_unit
            )
