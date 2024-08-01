from collections import OrderedDict

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoice_ids = super()._create_invoices(grouped=grouped, final=final, date=date)
        for invoice in invoice_ids:
            if invoice.line_ids and (
                len(invoice.line_ids.mapped(invoice.line_ids._get_section_grouping()))
                == 1
            ):
                # add section line for single group
                sequence = 10
                move_lines = invoice._get_ordered_invoice_lines()
                # Group move lines according to their sale order
                section_grouping_matrix = OrderedDict()
                for move_line in move_lines:
                    group = move_line._get_section_group()
                    section_grouping_matrix.setdefault(group, []).append(move_line.id)
                # Prepare section lines for each group
                section_lines = []
                for group, move_line_ids in section_grouping_matrix.items():
                    if group:
                        section_lines.append(
                            (
                                0,
                                0,
                                {
                                    "name": group._get_invoice_section_name(),
                                    "display_type": "line_section",
                                    "sequence": sequence,
                                    # see test: test_create_invoice_with_default_journal
                                    # forcing the account_id is needed to avoid
                                    # incorrect default value
                                    "account_id": False,
                                    # see test: test_create_invoice_with_currency
                                    # if the currency is not set with the right value
                                    # the total amount will be wrong
                                    # because all line do not have the same currency
                                    "currency_id": invoice.currency_id.id,
                                },
                            )
                        )
                        sequence += 10
                    for move_line in self.env["account.move.line"].browse(
                        move_line_ids
                    ):
                        move_line.sequence = sequence
                        sequence += 10
                invoice.line_ids = section_lines
        return invoice_ids
