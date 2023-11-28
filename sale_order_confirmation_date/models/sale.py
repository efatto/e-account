# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirmation_date = fields.Datetime(
        string="Confirmation date",
        readonly=True,
        index=True,
    )

    def _prepare_confirmation_values(self):
        date_order = self.date_order
        res = super(SaleOrder, self)._prepare_confirmation_values()
        res.update(date_order=date_order, confirmation_date=fields.Datetime.now())
        return res
