from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    nuts3_id = fields.Many2one(
        comodel_name="res.partner.nuts",
        string="Partner Region",
        readonly=True,
    )

    def _select_additional_fields(self, add_fields):
        add_fields["nuts3_id"] = ", partner.nuts3_id AS nuts3_id"
        return super()._select_additional_fields(add_fields)

    def _group_by_sale(self, groupby=""):
        groupby_ = super()._group_by_sale(groupby=groupby)
        groupby_ += " , partner.nuts3_id"
        return groupby_
