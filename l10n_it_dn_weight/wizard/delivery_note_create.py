from odoo import models


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _inherit = "stock.delivery.note.create.wizard"

    def _prepare_delivery_note_vals(self, sale_order_id):
        res = super()._prepare_delivery_note_vals(sale_order_id=sale_order_id)
        picking_ids = self.selected_picking_ids
        if picking_ids.stock_package_ids:
            # add first goods_appearance_id
            goods_appearance_id = picking_ids.mapped(
                "stock_package_ids.goods_appearance_id"
            )[:1]
            if goods_appearance_id:
                res["goods_appearance_id"] = goods_appearance_id.id
            # add dimension
            dimensions = []
            for pack in picking_ids.mapped("stock_package_ids"):
                if pack.dimensions or pack.goods_appearance_id:
                    if pack.dimensions and pack.goods_appearance_id:
                        dimensions.append(
                            f"{pack.goods_appearance_id.name} {pack.dimensions}"
                        )
                    elif pack.dimensions:
                        dimensions.append(f"{pack.dimensions}")
                    else:
                        dimensions.append(f"{pack.goods_appearance_id.name}")
            if dimensions:
                res["dimension"] = ", ".join(x for x in dimensions if x)
        return res
