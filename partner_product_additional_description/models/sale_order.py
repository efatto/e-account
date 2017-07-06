# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _has_additional_description(self):
        for line in self:
            line.has_additional_description = False
            if line.partner_product_additional_description:
                line.has_additional_description = True

    partner_product_additional_description = fields.Many2one(
        related='order_id.partner_id.partner_product_additional_description'
    )
    has_additional_description = fields.Boolean(
        compute=_has_additional_description,
    )