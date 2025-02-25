
from odoo import api, fields, models


class CashFlowForecastLine(models.Model):
    _inherit = "mis.cash_flow.forecast_line"

    sale_order_progress_id = fields.Many2one(
        comodel_name="sale.order.progress",
        ondelete="cascade",
        string="Sale order progress",
    )
    sale_progress_balance_forecast = fields.Float(
        compute="_compute_sale_balance_forecast",
        string="Sale progress forecast balance",
        store=True,
    )

    @api.depends(
        "sale_order_progress_id",
        "sale_balance_currency",
        "sale_order_progress_id.date",
        "sale_order_progress_id.order_id.currency_id.rate",
        "sale_order_progress_id.order_id.order_line.qty_invoiced",
        "sale_order_progress_id.amount_advance_toreturn",
        "sale_order_progress_id.amount_advance_returned",
        "sale_order_progress_id.amount_advance_invoiced",
        "sale_order_progress_id.amount_invoiced",
        "sale_line_id.qty_invoiced",
        "sale_line_id.product_uom_qty",
        "sale_line_id.qty_delivered",
        "sale_line_id.order_id.commitment_date",
        "sale_line_id.order_id.date_order",
        "sale_line_id.order_id.currency_id.rate",
        "sale_line_id.order_id.deposit_percent",
    )
    def _compute_sale_balance_forecast(self):
        progress_lines = self.filtered(lambda li: li.sale_order_progress_id)
        other_lines = self - progress_lines
        for line in progress_lines:
            line.sale_deposit_percent = (
                0 if line.sale_order_progress_id.is_advance else (
                    line.sale_order_progress_id.amount_advance_toreturn /
                    (line.sale_order_progress_id.amount_toinvoice or 1.0)
                )
            )
            line.sale_invoiced_percent = 1 if line.sale_order_progress_id.invoiced else (
                line.sale_order_progress_id.amount_advance_invoiced /
                (line.sale_order_progress_id.amount_advance_toinvoice or 1.0)
            ) if line.sale_order_progress_id.is_advance else (
                line.sale_order_progress_id.amount_invoiced /
                (line.sale_order_progress_id.amount_toinvoice or 1.0)
            )
            line.sale_progress_balance_forecast = (
                line.currency_id._convert(
                    (
                        (
                            line.sale_balance_currency
                            or line.balance
                        )
                        * (1 - line.sale_invoiced_percent)
                        * (1 - line.sale_deposit_percent)
                    ),
                    line.sale_order_progress_id.order_id.company_id.currency_id,
                    line.sale_order_progress_id.order_id.company_id,
                    line.sale_order_progress_id.date,
                )
            )
            line.balance = line.sale_progress_balance_forecast
        for line in other_lines:
            line.sale_progress_balance_forecast = 0
        super(CashFlowForecastLine, other_lines)._compute_sale_balance_forecast()
