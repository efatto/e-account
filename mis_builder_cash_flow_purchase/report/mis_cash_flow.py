# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class MisCashFlow(models.Model):
    _inherit = "mis.cash_flow"

    def get_cash_flow_query(self):
        query = super().get_cash_flow_query()
        if "purchase.order.line" not in query:
            purchase_query = """
                UNION ALL
                SELECT
                    fl.id as id,
                    'forecast_line' as line_type,
                    NULL as move_line_id,
                    fl.account_id as account_id,
                    CASE
                        WHEN fl.purchase_balance_forecast > 0
                        THEN fl.purchase_balance_forecast *
                            (1 - fl.purchase_invoiced_percent)
                        ELSE 0.0
                    END AS debit,
                    CASE
                        WHEN fl.purchase_balance_forecast < 0
                        THEN -fl.purchase_balance_forecast *
                            (1 - fl.purchase_invoiced_percent)
                        ELSE 0.0
                    END AS credit,
                    NULL as reconciled,
                    NULL as full_reconcile_id,
                    fl.partner_id as partner_id,
                    fl.company_id as company_id,
                    fl.name as name,
                    'posted' as state,
                    fl.date as date,
                    fl.res_model_id as res_model_id,
                    fl.res_id as res_id,
                    fl.purchase_invoiced_percent as invoiced_percent,
                    fl.currency_id as currency_id,
                    fl.purchase_balance_currency as balance_currency,
                    fl.purchase_balance_forecast as balance_forecast
                FROM mis_cash_flow_forecast_line as fl
                LEFT JOIN
                    ir_model im ON im.id = fl.res_model_id
                WHERE
                    im.model = 'purchase.order.line'
                UNION ALL
            """
            full_query = query.replace("UNION ALL", purchase_query, 1)
            return full_query
        return query
