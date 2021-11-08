# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _delivery_unset(self):
        # remove only if the same product
        for order in self:
            line_ids = order.order_line.filtered(
                lambda x: x.is_delivery and
                          x.product_id == x.order_id.carrier_id.product_id
            )
            line_ids.unlink()
