from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('general_discount')
    def onchange_general_discount(self):
        super().onchange_general_discount()
        self.mapped('order_line').filtered(
            lambda x: x.product_id.exclude_from_discount).update({
                'discount': 0.0,
            }
        )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
        if 'discount' in vals and 'order_id' in vals and 'product_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            if product.exclude_from_discount:
                vals['discount'] = 0.0
        return super().create(vals)

