# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_state = fields.Selection(
        [
            ("normal", "Margin missing or over maximum"),  # grey
            ("blocked", "Margin between mininum and zero"),  # red
            ("done", "Margin normal (between minimum and maximum)"),
        ],  # green
        string="Margin State",
        compute="_compute_margin_state",
        store=True,
    )

    @api.depends("margin", "price_subtotal")
    def _compute_margin_state(self):
        for line in self:
            margin_state = "normal"  # grey
            if line.margin and line.price_subtotal:
                margin_percent = (line.margin / line.price_subtotal) * 100
                if 0.0 < margin_percent < line.company_id.margin_min:
                    margin_state = "blocked"  # red
                if (
                    line.company_id.margin_min
                    <= margin_percent
                    <= line.company_id.margin_max
                ):
                    margin_state = "done"  # green
            line.margin_state = margin_state
