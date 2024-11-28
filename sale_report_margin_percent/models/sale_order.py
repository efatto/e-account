from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
                orders = self.search(order["__domain"])
                order["margin_percent"] = (
                    sum(orders.mapped('margin')) / (
                        sum(orders.mapped('amount_untaxed')) or 1
                    )
                )
        return res
