# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    move_price_to_invoice_total = fields.Float(
        help="This cost is only computed when products can be sold but not purchased "
             "and not produced.")

    @api.multi
    @api.depends('move_ids.price_unit')
    def _get_move_price_unit(self):
        for line in self:
            # preserve negative values as costs
            line.move_price_unit = min(
                [-abs(x.price_unit) for x in line.move_ids] or [0])
            if (
                line.product_id.purchase_ok
                or line.product_id.compute_pricelist_on_bom_component
            ):
                # this product can be purchased or its costs are computed from bom
                # components, so if we consider it, it would lead to a duplication of
                # costs
                line.move_price_to_invoice_total = 0
            else:
                line.move_price_to_invoice_total = (
                    line.move_price_unit if line.move_price_unit != 0.0 else
                    - line.product_standard_price) * (
                    max([line.qty_delivered, line.product_qty]) - line.qty_invoiced
                )
