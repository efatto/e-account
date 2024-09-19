from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped, final, date)

        for move in moves:
            if move.picking_ids.stock_package_ids:
                move.goods_appearance_id = self.picking_ids.mapped(
                    "stock_package_ids.goods_appearance_id"
                )[:1]
                dimensions = []
                for pack in self.picking_ids.mapped("stock_package_ids"):
                    if pack.dimensions or pack.goods_appearance_id:
                        if pack.dimensions and pack.goods_appearance_id:
                            dimensions.append(
                                f"{pack.goods_appearance_id.name} {pack.dimensions}"
                            )
                        elif pack.dimensions:
                            dimensions.append(f"{pack.dimensions}")
                        else:
                            dimensions.append(f"{pack.goods_appearance_id.name}")
                dimension = ", ".join(x for x in dimensions if x)
                if dimension:
                    move.dimension = dimension
            gross_weight_uom_id = self.env["stock.delivery.note"]._default_weight_uom()
            if gross_weight_uom_id:
                gross_weight_custom = sum(
                    pack.weight_custom_uom_id._compute_quantity(
                        qty=pack.weight_custom, to_unit=gross_weight_uom_id
                    )
                    for pack in self.picking_ids.mapped("stock_package_ids")
                )
                move.gross_weight_custom = gross_weight_custom

        return moves
