# -*- coding: utf-8 -*-

from openerp import models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def update_fiscal_position(self):
        for order in self:
            fp = order.fiscal_position
            for line in order.order_line:
                if line.product_id:
                    taxes = line.product_id.taxes_id
                    tax = fp.map_tax(taxes)
                    line.write({'tax_id': [(6, 0, tax.ids)]})
        return True
