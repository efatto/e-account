# Copyright 2023 Sergio Corato
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('margin', 'price_subtotal', 'product_id.exclude_from_margin')
    def _compute_margin_percent(self):
        super()._compute_margin_percent()
        for line in self.filtered(
                lambda x: x.product_id.exclude_from_margin
        ):
            line.margin_percent = 0.0

    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit',
                 'price_subtotal', 'product_id.exclude_from_margin')
    def _product_margin(self):
        super()._product_margin()
        for line in self.filtered(
                lambda x: x.product_id.exclude_from_margin
        ):
            line.margin = 0.0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('margin', 'order_line.margin', 'amount_untaxed',
                 'order_line.product_id.exclude_from_margin')
    def _compute_percent(self):
        super()._compute_percent()
        for order in self:
            if order.margin and order.amount_untaxed:
                order.percent = (
                    order.margin /
                    sum(
                        line.price_subtotal for line in order.order_line
                        if not line.product_id.exclude_from_margin
                    )
                ) * 100

    @api.depends('order_line.margin', 'order_line.product_id.exclude_from_margin')
    def _product_margin(self):
        super()._product_margin()
