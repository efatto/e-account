from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    confirmation_date = fields.Datetime(string="Confirmation date", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["confirmation_date"] = "s.confirmation_date"
        return res
