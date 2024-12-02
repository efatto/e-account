from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
        for order in res:
            if "__domain" in order and "margin_percent:avg" in fields:
                orders = self.search_read(
                    order["__domain"],
                    ["margin", "amount_untaxed"]
                )
                order["margin_percent"] = sum([x["margin"] for x in orders]) / (
                    sum([x["amount_untaxed"] for x in orders]) or 1
                ) * 100.0
        return res
