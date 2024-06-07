from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.picking_ids.stock_package_ids:
            res.update(
                goods_appearance_id=self.picking_ids.mapped(
                    "stock_package_ids.goods_appearance_id"
                )[:1],
                dimension=", ".join(
                    self.picking_ids.mapped("stock_package_ids.dimensions")
                ),
            )
        gross_weight_uom_id = self.env["stock.delivery.note"]._default_weight_uom()
        if gross_weight_uom_id:
            res.update(
                gross_weight_custom=sum(
                    pack.weight_custom_uom_id._compute_quantity(
                        qty=pack.weight_custom, to_unit=gross_weight_uom_id
                    )
                    for pack in self.picking_ids.mapped("stock_package_ids")
                ),
            )
        return res
