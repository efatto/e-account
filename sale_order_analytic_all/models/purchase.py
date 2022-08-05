# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _merge_in_existing_line(
            self, product_id, product_qty, product_uom, location_id, name, origin,
            values):
        super()._merge_in_existing_line(
            product_id=product_id, product_qty=product_qty, product_uom=product_uom,
            location_id=location_id, name=name, origin=origin, values=values)
        if values.get('sale_line_id') and self.sale_line_id \
                and values['sale_line_id'] != self.sale_line_id.id:
            # todo sembra solo la correzione di un errore, che succede quando?
            # check if self.sale_line_id is defined to decide if it's a dropshipping
            return False
        return True


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _update_purchase_order_line(
            self, product_id, product_qty, product_uom, values, line, partner):
        res = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, partner
        )
        procurement_uom_po_qty = product_uom._compute_quantity(
            product_qty, product_id.uom_po_id)
        # todo filter on what? this override RdP created for evaluation purposes
        #  modified to do not sum quantity already present in PO line, to use new value
        #  as the only value needed
        res.update(
            product_qty=procurement_uom_po_qty
        )
        return res
