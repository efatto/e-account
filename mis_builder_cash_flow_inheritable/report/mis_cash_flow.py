# Copyright 2019 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import fields, models, tools


class MisCashFlow(models.Model):
    _inherit = "mis.cash_flow"

    invoiced_percent = fields.Float()
    currency_id = fields.Many2one(comodel_name="res.currency")
    res_model_id = fields.Many2one(comodel_name="ir.model")
    balance_currency = fields.Float()
    balance_forecast = fields.Float()

    def get_cash_flow_query(self):
        query = """
            SELECT
                -- we use negative id to avoid duplicates and we don't use
                -- ROW_NUMBER() because the performance was very poor
                -aml.id as id,
                'move_line' as line_type,
                aml.id as move_line_id,
                aml.account_id as account_id,
                CASE
                    WHEN aml.amount_residual > 0
                    THEN aml.amount_residual
                    ELSE 0.0
                END AS debit,
                CASE
                    WHEN aml.amount_residual < 0
                    THEN -aml.amount_residual
                    ELSE 0.0
                END AS credit,
                aml.reconciled as reconciled,
                aml.full_reconcile_id as full_reconcile_id,
                aml.partner_id as partner_id,
                aml.company_id as company_id,
                aml.name as name,
                aml.parent_state as state,
                COALESCE(aml.date_maturity, aml.date) as date,
                Null as res_model_id,
                aml.id as res_id,
                0.0 as invoiced_percent,
                Null as currency_id,
                0.0 as balance_currency,
                0.0 as balance_forecast
            FROM account_move_line as aml
            WHERE aml.parent_state != 'cancel'
            UNION ALL
            SELECT
                fl.id as id,
                'forecast_line' as line_type,
                NULL as move_line_id,
                fl.account_id as account_id,
                CASE
                    WHEN fl.balance > 0
                    THEN fl.balance
                    ELSE 0.0
                END AS debit,
                CASE
                    WHEN fl.balance < 0
                    THEN -fl.balance
                    ELSE 0.0
                END AS credit,
                NULL as reconciled,
                NULL as full_reconcile_id,
                fl.partner_id as partner_id,
                fl.company_id as company_id,
                fl.name as name,
                'posted' as state,
                fl.date as date,
                Null as res_model_id,
                Null as res_id,
                0.0 as invoiced_percent,
                Null as currency_id,
                0.0 as balance_currency,
                0.0 as balance_forecast
            FROM mis_cash_flow_forecast_line as fl
            WHERE fl.res_model_id IS NULL
        """
        return query

    def init(self):
        query = self.get_cash_flow_query()
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW %s as %s", (AsIs(self._table), AsIs(query))
        )
