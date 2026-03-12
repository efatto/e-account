from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _get_section_group(self):
        """Group invoice lines according to uninvoiced delivery pickings"""
        group = super()._get_section_group()
        # If the product is not linked to a delivery note, put in the same group of a dn
        # with the same sale order.
        # todo remove lines with type section or notes? or move at the end?
        invoice_section_grouping = self.company_id.invoice_section_grouping
        if (
            invoice_section_grouping == "delivery_note_sale"
            and not self.sale_line_ids.delivery_note_line_ids
        ):
            delivery_notes_same_sale_order = self.env["stock.delivery.note"].search(
                [
                    (
                        "picking_ids.sale_id",
                        "in",
                        self.sale_line_ids.mapped("order_id").ids,
                    ),
                ]
            )
            group = group.filtered(
                lambda dn: dn.id in delivery_notes_same_sale_order.ids
            )
            if not group:
                # lines are processed in a random order, so we add the first dn found
                group = delivery_notes_same_sale_order[:1]
            if not group:
                group = self.sale_line_ids.mapped("order_id")
        return group

    def _get_section_grouping(self):
        invoice_section_grouping = self.company_id.invoice_section_grouping
        if invoice_section_grouping == "delivery_note_sale":
            return "sale_line_ids.delivery_note_line_ids.delivery_note_id"
        return super()._get_section_grouping()
