# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def open_sale_order_lines(self):
        self.ensure_one()
        action_name = 'sale_order_line_menu_usability.action_order_line_tree2'
        action = self.env.ref(action_name)
        action = action.read()[0]
        action['domain'] = [('id', 'in', self.order_line.ids)]
        return action
