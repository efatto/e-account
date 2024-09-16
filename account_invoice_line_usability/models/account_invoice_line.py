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
        string="Move Price Unit", compute='_get_move_price_unit',
        inverse='_set_move_price_unit', store=True)
    move_price_total = fields.Float(
        string="Price Total", compute='_get_move_price_unit', store=False)

    @api.multi
    @api.depends('move_line_ids.price_unit')
    def _get_move_price_unit(self):
        for line in self:
            line.move_price_unit = min(
                [-abs(x.price_unit) for x in line.move_line_ids] or [0])
            line.move_price_total = line.quantity * (
                line.move_price_unit if line.move_price_unit != 0.0 else
                - line.product_standard_price)

    @api.one
    def _set_move_price_unit(self):
        if self.move_line_ids and self.move_price_unit:
            for move_line in self.move_line_ids:
                move_line.price_unit = self.move_price_unit
