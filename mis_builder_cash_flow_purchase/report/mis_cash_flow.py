# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class MisCashFlow(models.Model):
    _inherit = 'mis.cash_flow'

    def get_cash_flow_query(self):
        query = super().get_cash_flow_query()
        query.replace(
            "UNION ALL",
            """
            UNION ALL
            SELECT
                fl.id as id,
                CAST('forecast_line' AS varchar) as line_type,
                Null as move_line_id,
                fl.account_id as account_id,
                CASE
                    WHEN fl.purchase_balance_forecast > 0
                    THEN fl.purchase_balance_forecast
                    ELSE 0.0
                END AS debit,
                CASE
                    WHEN fl.purchase_balance_forecast < 0
                    THEN -fl.purchase_balance_forecast
                    ELSE 0.0
                END AS credit,
                Null as reconciled,
                Null as full_reconcile_id,
                fl.partner_id as partner_id,
                fl.company_id as company_id,
                %i as user_type_id,
                fl.name as name,
                fl.date as date,
                im.model AS res_model,
                fl.res_id as res_id,
                fl.purchase_invoiced_percent AS invoiced_percent,
                cu.id AS currency_id,
                cu.rate AS currency_rate,
                fl.purchase_balance_currency AS balance_currency,
                fl.purchase_balance_forecast AS balance_forecast
            FROM mis_cash_flow_forecast_line as fl
            LEFT JOIN
                ir_model im ON im.id = fl.res_model_id
            LEFT JOIN
                purchase_order_line pol ON pol.id = fl.purchase_line_id
            LEFT JOIN
                purchase_order po ON po.id = pol.order_id
            LEFT JOIN
                currency_id cu ON cu.id = po.currency_id
            WHERE
                im.model = 'purchase_order_line'
            UNION ALL
            """
        )
        return query
