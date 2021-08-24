# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    account_code = fields.Char(
        related='account_id.code')
    product_standard_price = fields.Float(
        related='product_id.standard_price')
    move_price_unit = fields.Float(
        string="Move Price Unit", compute='_get_move_price_unit', store=True)
    move_price_total = fields.Float(
        string="Price Total", compute='_get_move_price_unit', store=True)

    @api.multi
    @api.depends('move_line_ids.price_unit')
    def _get_move_price_unit(self):
        for line in self:
            line.move_price_unit = max(line.move_line_ids.mapped('price_unit') or [0])
            line.move_price_total = line.quantity * (
                line.move_price_unit if line.move_price_unit != 0.0 else
                - line.product_standard_price)
