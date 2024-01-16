# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class CashFlowForecastLine(models.Model):
    _inherit = "mis.cash_flow.forecast_line"

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        ondelete="cascade",
        string="Sale order line",
    )
    sale_balance_currency = fields.Monetary(
        currency_field="currency_id",
        help="Sale amount in vendor currency recomputed with delivered qty",
    )
    sale_invoiced_percent = fields.Float(
        compute="_compute_sale_balance_forecast", store=True
    )
    sale_balance_forecast = fields.Float(
        compute="_compute_sale_balance_forecast",
        string="Sale forecast balance",
        store=True,
    )

    @api.depends(
        "sale_balance_currency",
        "sale_line_id.qty_invoiced",
        "sale_line_id.product_uom_qty",
        "sale_line_id.qty_delivered",
        "sale_line_id.order_id.commitment_date",
        "sale_line_id.order_id.date_order",
        "sale_line_id.order_id.currency_id.rate",
    )
    def _compute_sale_balance_forecast(self):
        for line in self:
            if line.sale_line_id:
                line.sale_invoiced_percent = line.sale_line_id.qty_invoiced / (
                    max(
                        [
                            line.sale_line_id.product_uom_qty,
                            line.sale_line_id.qty_delivered,
                            1,
                        ]
                    )
                )
                line.sale_balance_forecast = line.currency_id._convert(
                    line.sale_balance_currency or line.balance,
                    line.sale_line_id.order_id.company_id.currency_id,
                    line.sale_line_id.order_id.company_id,
                    line.date,
                ) * (1 - line.sale_invoiced_percent)
                line.balance = line.sale_balance_forecast
            else:
                line.sale_invoiced_percent = 0
                line.sale_balance_forecast = line.balance
