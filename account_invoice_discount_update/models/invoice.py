from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    discount = fields.Float()

    @api.depends("discount", "invoice_line_ids")
    def invoice_discount_update(self):
        for invoice in self:
            lines = invoice.invoice_line_ids.filtered(
                lambda x: x.product_id.type != "service"
            )
            for line in lines:
                line.with_context(check_move_validity=False).update(
                    {"discount": invoice.discount}
                )
            invoice._sync_dynamic_lines(container={"records": invoice, "self": invoice})
