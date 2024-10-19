from odoo import models, api, fields

# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     @api.multi
#     def button_release(self):
#         res = super().button_release()
#         for purchase in self:
#             purchase.mapped(
#                 "picking_ids.move_lines.move_dest_ids"
#             )._compute_purchase_ordered_qty()
#         return res
#
#
# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     @api.multi
#     def action_assign(self):
#         result = super().action_assign()
#         for production in self:
#             production.move_raw_ids._compute_purchase_ordered_qty()
#         return result


# in procurement.group.run() c'è values che contiene dest_ids

class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_ordered_qty = fields.Float(
        string='Purchase Ordered Qty',
        compute="_compute_purchase_ordered_qty",
    )
    move_child_ids = fields.Many2many(
        comodel_name='stock.move',
        relation="stock_move_child_ids_rel",
        column1="move_origin_id",
        column2="move_child_id",
        copy=False,
        string="Child Moves",
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for move in res:
            for move_dest in move.move_dest_ids:
                if move_dest.raw_material_production_id:
                    move_dest.write({
                        "move_child_ids": [(6, 0, move.ids)],
                    })
        return res

    @api.depends("move_child_ids", "state", "move_line_ids", "group_id")
    def _compute_purchase_ordered_qty(self):
        moves = self.filtered(lambda m: m.raw_material_production_id and m.move_child_ids)
        for move in (self - moves):
            move.purchase_ordered_qty = 0
        for move in moves:
            # search the move lines created from purchase orders for production refill
            # recs = self.env["stock.move.line"].search_read(
            #     domain=[
            #         ("state", "=", "assigned"),
            #         ("move_id.raw_material_production_id", "=", False),
            #         ("product_id", "=", move.product_id.id),
            #         ("move_id.group_id", "=",
            #          move.raw_material_production_id.procurement_group_id.id),
            #         ("location_id.usage", "=", "supplier"),
            #         ("location_dest_id.usage", "=", "internal"),
            #     ],
            #     fields=["product_qty"]
            # )
            # purchase_ordered_qty = sum(rec.get("product_qty") for rec in recs)
            purchase_ordered_qty = sum(move.mapped('move_child_ids.move_line_ids.product_qty'))
            move.purchase_ordered_qty = purchase_ordered_qty
