# Copyright 2023 Sergio Corato
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "price_subtotal",
        "product_uom_qty",
        "purchase_price",
        "product_id",
        "product_id.exclude_from_margin",
        "price_unit",
    )
    def _compute_margin(self):
        super()._compute_margin()
        for line in self.filtered(lambda sol: sol.product_id.exclude_from_margin):
            line.margin = 0.0
            line.margin_percent = 0.0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "order_line.margin",
        "amount_untaxed",
        "order_line.product_id.exclude_from_margin",
    )
    def _compute_margin(self):
        super()._compute_margin()
        for order in self.filtered(
            lambda so: any(sol.product_id.exclude_from_margin for sol in so.order_line)
        ):
            if order.margin and order.amount_untaxed:
                order.margin_percent = order.margin / sum(
                    line.price_subtotal
                    for line in order.order_line
                    if not line.product_id.exclude_from_margin
                )
