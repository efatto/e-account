from odoo import api, models


class StockDeliveryNote(models.Model):
    _inherit = "stock.delivery.note"

    @api.depends("picking_ids")
    def _compute_weights(self):
        super()._compute_weights()
        gross_weight_uom_id = self.env["stock.delivery.note"]._default_weight_uom()
        for note in self:
            # sum weight from pickings
            if note.picking_ids.stock_package_ids:
                if gross_weight_uom_id:
                    gross_weight_custom = sum(
                        pack.weight_custom_uom_id._compute_quantity(
                            qty=pack.weight_custom, to_unit=gross_weight_uom_id
                        )
                        for pack in note.picking_ids.mapped("stock_package_ids")
                    )
                    note.gross_weight = gross_weight_custom
                    note.net_weight = gross_weight_custom
