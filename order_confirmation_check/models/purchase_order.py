
from odoo import _, fields, models, tools


from .check_order_mixin import check_attachment


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "check.order.mixin.parent"]

    def button_check_attachment(self):
        self.ensure_one()
        check_attachment(self, self.order_line)
