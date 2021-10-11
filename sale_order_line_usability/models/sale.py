# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_standard_price = fields.Float(
        string="Product Cost", related='product_id.standard_price')
    move_price_unit = fields.Float(
        string="Move Cost Unit", compute='_get_move_price_unit', store=True)
    move_price_to_invoice_total = fields.Float(
        string="Total Cost To Invoice", compute='_get_move_price_unit', store=False)

    @api.multi
    @api.depends('move_ids.price_unit')
    def _get_move_price_unit(self):
        for line in self:
            # preserve negative values as costs
            line.move_price_unit = min(
                [-abs(x.price_unit) for x in line.move_ids] or [0])
            line.move_price_to_invoice_total = (
                line.move_price_unit if line.move_price_unit != 0.0 else
                - line.product_standard_price) * (
                max([line.qty_delivered, line.product_qty]) - line.qty_invoiced
            )
