from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    confirmation_date = fields.Datetime(
        string="Confirmation date",
        readonly=True)

    def _select_additional_fields(self, add_fields):
        add_fields["confirmation_date"] = ", s.confirmation_date AS confirmation_date"
        return super()._select_additional_fields(add_fields)
