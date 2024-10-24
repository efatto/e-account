
from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_release(self):
        for order in self:
            if order.requisition_id:
                # set move_dest_ids as only 1 can be set! and the default logic set
                # this value n times until only the last order has the value set
                for order_line in order.order_line:
                    for pr_line in order.requisition_id.line_ids.filtered(
                        lambda l: l.product_id == order_line.product_id
                    ):
                        order_line.write({
                            "move_dest_ids": pr_line.move_dest_id and
                            [(4, pr_line.move_dest_id.id)] or [],
                        })
        super().button_release()
