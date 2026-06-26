from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    nuts3_id = fields.Many2one(
        comodel_name="res.partner.nuts",
        string="Partner Region",
        readonly=True,
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["nuts3_id"] = "partner.nuts3_id"
        return res

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale()
        res += ", partner.nuts3_id"
        return res
