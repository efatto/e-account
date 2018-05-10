# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends('default_sale_discount', 'order_line')
    def sale_discount_update(self):
        for order in self:
            for line in order.order_line.filtered(
                lambda x: x.product_id.service_type not in [
                    'other', 'contribution', 'discount', 'transport']
            ):
                line.discount = order.default_sale_discount
                line.complex_discount = order.default_sale_complex_discount
