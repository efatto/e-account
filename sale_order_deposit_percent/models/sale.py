from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deposit_percent = fields.Float(
        compute="_compute_deposit_percent", store=True,
    )

    @api.depends(
        "order_line.product_id",
        "order_line.qty_invoiced",
        "order_line.product_uom_qty",
        "order_line.qty_delivered",
        "amount_untaxed",
    )
    def _compute_deposit_percent(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param(
            'sale.default_deposit_product_id')
        deposit_product = self.env['product.product'].browse(int(product_id)).exists()
        for order in self:
            deposit_percent = 0
            deposit_lines = order.order_line.filtered(
                lambda x: x.product_id == deposit_product
            )
            deposit_amount = sum(
                [
                    x._get_price_with_discount(x.price_unit) * x.qty_invoiced
                    for x in deposit_lines
                ]
            )
            if order.amount_untaxed and deposit_amount:
                deposit_percent = deposit_amount / order.amount_untaxed
            order.deposit_percent = deposit_percent


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_price_with_discount(self, price):
        price = price * (1 - self.discount / 100.0)
        if hasattr(self, 'discount2') and hasattr(self, 'discount3'):
            price = price * (1 - self.discount2 / 100.0)
            price = price * (1 - self.discount3 / 100.0)
        return price
