# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _get_price_unit_net(self):
        for line in self:
            line.price_unit_net = line.price_subtotal / (
                line.product_uom_qty if line.product_uom_qty != 0 else 1)

    price_unit_net = fields.Float(compute=_get_price_unit_net)