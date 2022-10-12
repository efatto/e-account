# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.margin')
    def _product_margin(self):
        if self.env.in_onchange:
            for order in self:
                order.margin = sum(
                    order.order_line.mapped('margin'))
        else:
            # On batch records recomputation (e.g. at install), compute the margins
            # with a single read_group query for better performance.
            # This isn't done in an onchange environment because (part of) the data
            # may not be stored in database (new records or unsaved modifications).
            grouped_order_lines_data = self.env['sale.order.line'].read_group(
                [
                    ('order_id', 'in', self.ids),
                ], ['margin', 'order_id'], ['order_id'])
            for data in grouped_order_lines_data:
                order = self.browse(data['order_id'][0])
                order.margin = data['margin']
