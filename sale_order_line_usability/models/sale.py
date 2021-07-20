# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_standard_price = fields.Float(related='product_id.standard_price')
    move_price_unit = fields.Float(
        string="Move Price Unit", compute='_get_move_price_unit', store=True,
    )

    @api.multi
    @api.depends('move_ids.price_unit')
    def _get_move_price_unit(self):
        for line in self:
            line.move_price_unit = max(line.move_ids.mapped('price_unit') or [0])
