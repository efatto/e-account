from odoo import models


class MisCashFlow(models.Model):
    _inherit = "mis.cash_flow"

    def get_cash_flow_query(self):
        query = super().get_cash_flow_query()
        account_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        if "stock.move" not in query:  # todo correggere la query
            mrp_query = """
                UNION ALL
                SELECT
                    fl.id as id,
                    'forecast_line' as line_type,
                    NULL as move_line_id,
                    fl.account_id as account_id,
                    CASE
                        WHEN fl.mrp_balance_forecast > 0
                        THEN fl.mrp_balance_forecast *
                            (1 - fl.mrp_reserved_percent)
                        ELSE 0.0
                    END AS debit,
                    CASE
                        WHEN fl.mrp_balance_forecast < 0
                        THEN -fl.mrp_balance_forecast *
                            (1 - fl.mrp_reserved_percent)
                        ELSE 0.0
                    END AS credit,
                    NULL as reconciled,
                    NULL as full_reconcile_id,
                    fl.partner_id as partner_id,
                    fl.company_id as company_id,
                    %i as user_type_id,
                    fl.name as name,
                    'posted' as state,
                    fl.date as date,
                    fl.res_model_id as res_model_id,
                    fl.res_id as res_id,
                    fl.mrp_reserved_percent as invoiced_percent,
                    fl.currency_id as currency_id,
                    fl.mrp_balance_currency as balance_currency,
                    fl.mrp_balance_forecast as balance_forecast
                FROM mis_cash_flow_forecast_line as fl
                LEFT JOIN
                    ir_model im ON im.id = fl.res_model_id
                LEFT JOIN
                    stock_move sm ON sm.id = fl.res_id
                LEFT JOIN
                    mrp_production mp ON mp.id = sm.raw_material_production_id
                WHERE
                    im.model = 'stock.move'
                UNION ALL
            """ % account_type_receivable.id
            full_query = query.replace("UNION ALL", mrp_query, 1)
            return full_query
        return query
