# Copyright 2019 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools
from psycopg2.extensions import AsIs


class MisCashFlow(models.Model):
    _inherit = 'mis.cash_flow'

    invoiced_percent = fields.Float()
    currency_id = fields.Many2one(
        comodel_name='res.currency'
    )
    res_model = fields.Char()
    balance_currency = fields.Float()
    balance_forecast = fields.Float()

    def get_cash_flow_query(self):
        account_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        query = """
            SELECT
                -- we use negative id to avoid duplicates and we don't use
                -- ROW_NUMBER() because the performance was very poor
                -aml.id as id,
                CAST('move_line' as varchar) as line_type,
                aml.id as move_line_id,
                aml.account_id as account_id,
                CASE
                    WHEN aml.amount_residual > 0
                    THEN aml.amount_residual
                    ELSE 0.0
                END as debit,
                CASE
                    WHEN aml.amount_residual < 0
                    THEN -aml.amount_residual
                    ELSE 0.0
                END as credit,
                aml.reconciled as reconciled,
                aml.full_reconcile_id as full_reconcile_id,
                aml.partner_id as partner_id,
                aml.company_id as company_id,
                aml.user_type_id as user_type_id,
                aml.name as name,
                aml.date_maturity as date,
                CAST('account_move_line' as varchar) as res_model,
                aml.id as res_id,
                0.0 as invoiced_percent,
                Null as currency_id,
                0.0 as balance_currency,
                0.0 as balance_forecast
            FROM account_move_line as aml
            UNION ALL
            SELECT
                fl.id as id,
                CAST('forecast_line' as varchar) as line_type,
                Null as move_line_id,
                fl.account_id as account_id,
                CASE
                    WHEN fl.balance > 0
                    THEN fl.balance
                    ELSE 0.0
                END as debit,
                CASE
                    WHEN fl.balance < 0
                    THEN -fl.balance
                    ELSE 0.0
                END as credit,
                Null as reconciled,
                Null as full_reconcile_id,
                fl.partner_id as partner_id,
                fl.company_id as company_id,
                %i as user_type_id,
                fl.name as name,
                fl.date as date,
                Null as res_model,
                Null as res_id,
                0.0 as invoiced_percent,
                Null as currency_id,
                0.0 as balance_currency,
                0.0 as balance_forecast
            FROM mis_cash_flow_forecast_line as fl
            LEFT JOIN
                ir_model im ON im.id = fl.res_model_id
            WHERE
                fl.res_model_id IS NULL
        """ % account_type_receivable.id
        return query

    @api.model_cr
    def init(self):
        query = self.get_cash_flow_query()
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            'CREATE OR REPLACE VIEW %s as %s',
            (AsIs(self._table), AsIs(query))
        )
