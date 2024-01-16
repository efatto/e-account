# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class CashFlowForecastLine(models.Model):
    _inherit = "mis.cash_flow.forecast_line"

    purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        ondelete="cascade",
        string="Purchase order line",
    )
    purchase_balance_currency = fields.Monetary(
        currency_field="currency_id",
        help="Purchase amount in vendor currency recomputed with delivered qty",
    )
    purchase_invoiced_percent = fields.Float(
        compute="_compute_purchase_balance_forecast", store=True
    )
    purchase_balance_forecast = fields.Float(
        compute="_compute_purchase_balance_forecast",
        string="Purchase forecast balance",
        store=True,
    )

    @api.depends(
        "balance",
        "purchase_balance_currency",
        "purchase_line_id.qty_invoiced",
        "purchase_line_id.product_qty",
        "purchase_line_id.qty_received",
        "purchase_line_id.order_id.date_planned",
        "purchase_line_id.order_id.date_order",
        "purchase_line_id.order_id.currency_id.rate",
    )
    def _compute_purchase_balance_forecast(self):
        for line in self:
            if line.purchase_line_id:
                purchase_invoiced_percent = line.purchase_line_id.qty_invoiced / (
                    max(
                        line.purchase_line_id.product_qty,
                        line.purchase_line_id.qty_received,
                        1,
                    )
                )
                line.purchase_invoiced_percent = min(purchase_invoiced_percent, 1)
                line.purchase_balance_forecast = -line.currency_id._convert(
                    line.purchase_balance_currency or line.balance,
                    line.purchase_line_id.order_id.company_id.currency_id,
                    line.purchase_line_id.order_id.company_id,
                    line.date,
                ) * (1 - line.purchase_invoiced_percent)
            else:
                line.purchase_invoiced_percent = 0
                line.purchase_balance_forecast = line.balance
