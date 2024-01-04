# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class MisCashFlow(models.Model):
    _inherit = "mis.cash_flow"

    def get_cash_flow_query(self):
        query = super().get_cash_flow_query()
        account_type_receivable = self.env.ref("account.data_account_type_receivable")
        purchase_query = (
            """
            UNION ALL
            SELECT
                fl.id as id,
                CAST('forecast_line' as varchar) as line_type,
                Null as move_line_id,
                fl.account_id as account_id,
                CASE
                    WHEN fl.purchase_balance_forecast > 0
                    THEN fl.purchase_balance_forecast *
                        (1 - fl.purchase_invoiced_percent)
                    ELSE 0.0
                END as debit,
                CASE
                    WHEN fl.purchase_balance_forecast < 0
                    THEN -fl.purchase_balance_forecast *
                        (1 - fl.purchase_invoiced_percent)
                    ELSE 0.0
                END as credit,
                Null as reconciled,
                Null as full_reconcile_id,
                fl.partner_id as partner_id,
                fl.company_id as company_id,
                %i as user_type_id,
                fl.name as name,
                fl.date as date,
                CAST('purchase_order_line' as varchar) as res_model,
                fl.res_id as res_id,
                fl.purchase_invoiced_percent as invoiced_percent,
                fl.currency_id as currency_id,
                fl.purchase_balance_currency as balance_currency,
                fl.purchase_balance_forecast as balance_forecast
            FROM mis_cash_flow_forecast_line as fl
            UNION ALL
        """
            % account_type_receivable.id
        )
        full_query = query.replace("UNION ALL", purchase_query)
        return full_query
