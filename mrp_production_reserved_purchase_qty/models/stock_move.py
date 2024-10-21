from odoo import models, api, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_ordered_qty = fields.Float(
        string='Purchase Ordered Qty',
        compute="_compute_purchase_ordered_qty",
        store=True,
    )

    @api.depends(
        "move_orig_ids",
        "move_orig_ids.move_line_ids",
        "move_orig_ids.move_line_ids.product_qty",
        "move_orig_ids.purchase_line_id.procurement_group_id",
        "state",
        "raw_material_production_id",
        "group_id",
    )
    def _compute_purchase_ordered_qty(self):
        moves = self.filtered(
            lambda m: m.raw_material_production_id and m.move_orig_ids
            and m.move_orig_ids.purchase_line_id.procurement_group_id == m.group_id
        )
        for move in (self - moves):
            move.purchase_ordered_qty = 0
        for move in moves:
            purchase_ordered_qty = sum(
                move.mapped('move_orig_ids.move_line_ids.product_qty'))
            move.purchase_ordered_qty = purchase_ordered_qty
