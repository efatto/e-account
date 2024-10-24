# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CashFlowForecastLine(models.Model):
    _inherit = 'mis.cash_flow.forecast_line'
    _rec_name = 'date'

    res_id = fields.Integer()
    res_model_id = fields.Many2one(
        comodel_name='ir.model',
        index=True)
    res_model = fields.Char(
        related='res_model_id.model',
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency'
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Analytic Account",
    )
