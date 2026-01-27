from odoo import models

from .check_order_mixin import check_attachment


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "check.order.mixin.parent"]

    def button_check_attachment(self):
        self.ensure_one()
        check_attachment(self, self.order_line)
