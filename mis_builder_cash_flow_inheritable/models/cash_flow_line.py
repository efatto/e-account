# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CashFlowForecastLine(models.Model):
    _inherit = "mis.cash_flow.forecast_line"
    _rec_name = "date"

    res_id = fields.Integer()
    res_model_id = fields.Many2one(comodel_name="ir.model", index=True)
    res_model = fields.Char(related="res_model_id.model", store=True)
    currency_id = fields.Many2one(comodel_name="res.currency")


class CashFlowMixin(models.AbstractModel):
    _name = "mis.cash_flow.mixin"
    _description = "Cash Flow Mixin"

    company_id = fields.Many2one(comodel_name="res.company")

    def _get_account(self, account_ref):
        """
        account_ref: str
        Return account id for given account_ref.
        """
        chart_template = self.with_context(
            allowed_company_ids=self.company_id.root_id.ids
        ).env["account.chart.template"]
        outstanding_account_id = (
            chart_template.ref(account_ref, raise_if_not_found=False)
            or self.env["account.account"].search(
                [
                    (
                        "account_type",
                        "=",
                        "asset_cash",
                    ),
                    ("company_ids", "in", self.company_id.id),
                ],
                limit=1,
            )
        ).id
        return outstanding_account_id
