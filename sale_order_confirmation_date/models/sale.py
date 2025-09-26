from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirmation_date = fields.Datetime(
        string="Confirmation date",
        readonly=True,
        index=True,
        copy=False,
    )

    def _prepare_confirmation_values(self):
        res = super()._prepare_confirmation_values()
        # do not override date_order and put confirmation_date instead
        res.pop("date_order")
        res.update(confirmation_date=fields.Datetime.now())
        return res
