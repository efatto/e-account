from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        default = dict(default or {})
        if self.purchase_price and self.env.context.get("preserve_purchase_price"):
            default["purchase_price"] = self.purchase_price
        return super().copy_data(default=default)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def copy_revision_with_context(self):
        default_data = self.default_get([])
        new_rev_number = max(self.old_revision_ids.mapped("revision_number") or [0]) + 1
        default_data.update(
            {
                "active": False,
                "state": "cancel",
                "revision_number": new_rev_number,
                "unrevisioned_name": self.unrevisioned_name,
                "name": self.name,
                "client_order_ref": self.client_order_ref,
            }
        )
        self.write(
            {
                "state": "draft",
                # revision_number of active so is unchanged (always 0), as there is a
                # sql constraint that forbid to write the same number, even if modified
                # later
                # 'revision_number': new_rev_number,
                "name": "%s-%02d" % (self.unrevisioned_name, new_rev_number),
            }
        )
        default_data["order_line"] = [
            (0, 0, line.with_context(preserve_purchase_price=True).copy_data()[0])
            for line in self.order_line
        ]
        new_revision = self.copy(default_data)
        self.old_revision_ids.write(
            {
                "current_revision_id": self.id,
            }
        )
        self.write(
            {
                "old_revision_ids": [(4, new_revision.id)],
            }
        )

        return new_revision

    def create_revision(self):
        super().create_revision()
        return True
