
from odoo import api, fields, models


class CashFlowForecastLine(models.Model):
    _inherit = "mis.cash_flow.forecast_line"

    sale_order_progress_id = fields.Many2one(
        comodel_name="sale.order.progress",
        ondelete="cascade",
        string="Sale order progress",
    )
    sale_progress_balance_forecast = fields.Float(
        compute="_compute_sale_progress_balance_forecast",
        string="Sale progress forecast balance",
        store=True,
    )

    @api.depends(
        "sale_order_progress_id",
        "sale_balance_currency",
        "sale_order_progress_id.date",
        "sale_order_progress_id.order_id.currency_id.rate",
    )
    def _compute_sale_progress_balance_forecast(self):
        for line in self:
            if line.sale_order_progress_id:
                line.sale_progress_balance_forecast = (
                    line.currency_id._convert(
                        (
                            (
                                line.sale_balance_currency
                                or line.balance
                            )
                        ),
                        line.sale_order_progress_id.order_id.company_id.currency_id,
                        line.sale_order_progress_id.order_id.company_id,
                        line.sale_order_progress_id.date,
                    )
                )
                line.balance = line.sale_progress_balance_forecast
            else:
                line.sale_progress_balance_forecast = 0
