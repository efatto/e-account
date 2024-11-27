
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin_percent_order = fields.Float(
        string="Margin Order (%)", readonly=True, group_operator="avg")
    margin_percent_line = fields.Float(
        string="Margin Line (%)", readonly=True, group_operator="avg")

    def _select_additional_fields(self, fields):
        fields['margin_percent_order'] = (
            ", MAX(s.margin_percent * 100.0) AS margin_percent_order"
        )
        fields['margin_percent_line'] = (
            ", MAX(l.margin_percent * 100.0) AS margin_percent_line"
        )
        return super()._select_additional_fields(fields)
