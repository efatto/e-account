# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    account_code = fields.Char(related="account_id.code")
    product_standard_price = fields.Float(related="product_id.standard_price")
    move_price_unit = fields.Float(
        string="Unit Cost", compute="_compute_move_price_unit", store=True
    )
    move_price_total = fields.Float(
        string="Total Cost", compute="_compute_move_price_unit", store=True
    )

    @api.depends("move_line_ids.price_unit", "product_id", "product_id.standard_price")
    def _compute_move_price_unit(self):
        invoice_lines = self.filtered(
            lambda x: x.move_id.move_type
            in ["out_invoice", "out_refund", "in_invoice", "in_refund"]
        )
        for not_invoice_line in self - invoice_lines:
            not_invoice_line.move_price_unit = 0
            not_invoice_line.move_price_total = 0
        for line in invoice_lines:
            if not line.product_id:
                price_unit = 0
            else:
                price_unit = min(
                    [-abs(x.price_unit) for x in line.move_line_ids] or [0]
                )
                if not price_unit:
                    price_unit = -line.product_id.standard_price
            line.move_price_unit = price_unit
            line.move_price_total = line.quantity * line.move_price_unit
