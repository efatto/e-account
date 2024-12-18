from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    margin_percent_weighted = fields.Float(
        string="Margin Weighted (%)", readonly=True, group_operator="avg"
    )

    def _select_additional_fields(self, fields):
        fields[
            "margin_percent_weighted"
        ] = ", MAX(s.margin_percent * 100.0) AS margin_percent_weighted"
        return super()._select_additional_fields(fields)

    @api.model
    def read_group(
        self,
        domain,
        fields,
        groupby,
        offset=0,
        limit=None,
        orderby=False,
        lazy=True,
    ):
        res = super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        for order_line in res:
            if "__domain" in order_line and "margin_percent_weighted:avg" in fields:
                order_lines = self.search_read(
                    order_line["__domain"], ["margin", "price_subtotal"]
                )
                margin_percent = (
                    sum([x["margin"] for x in order_lines])
                    / (sum([x["price_subtotal"] for x in order_lines]) or 1)
                    * 100.0
                )
                order_line["margin_percent_weighted"] = margin_percent
        return res
