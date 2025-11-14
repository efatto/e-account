import re

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_insert_intrastat_data_invoice(self):
        get_intrastat_info = self.env["get.intrastat.info"]
        for move in self.filtered(lambda x: x.move_type.startswith("out_")):
            intrastat_info = {}
            for line in move.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.type != "service"
            ):
                intrastat_text, intrastat_info = get_intrastat_info._get_info(
                    line.product_id,
                    line.quantity,
                    line.price_subtotal,
                    intrastat_info,
                )
                if "HS CODE" in line.name:
                    line.name = re.compile("\nHS CODE.*").sub("", line.name)
                line.name += intrastat_text
            if "HS Codes:" in move.narration:
                move.narration = re.compile("\nHS Codes:.*").sub("", move.narration)
                move.narration = re.compile("\n[0-9]{4,12}: .*€").sub(
                    "", move.narration
                )
            move.narration = get_intrastat_info._get_narration(intrastat_info)

    def action_remove_intrastat_data_invoice(self):
        for move in self.filtered(lambda x: x.move_type.startswith("out_")):
            for line in move.invoice_line_ids.filtered(
                lambda x: x.product_id
                and x.product_id.type != "service"
                and "HS CODE" in x.name
            ):
                line.name = re.compile("\nHS CODE.*").sub("", line.name)
            if "HS Codes:" in move.narration:
                move.narration = re.compile("\nHS Codes:.*").sub("", move.narration)
                move.narration = re.compile("\n[0-9]{4,12}: .*€").sub(
                    "", move.narration
                )
