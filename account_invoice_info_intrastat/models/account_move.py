import re

from odoo import models
from odoo.tools import float_round, get_lang


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_insert_intrastat_data_invoice(self):
        precision_weight_digits = (
            self.env["decimal.precision"].search([("name", "=", "Stock Weight")]).digits
        )
        for move in self.filtered(lambda x: x.move_type.startswith("out_")):
            intrastat_info = {}
            lang = get_lang(self.env, lang_code=self.env.company.partner_id.lang)
            for line in move.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.type != "service"
            ):
                # if country of origin is not found in product, get from first seller
                # of the product and eventually from the current company
                country_name = (
                    line.product_id.intrastat_country_origin_id
                    and line.product_id.intrastat_country_origin_id.with_context(
                        lang="en_US"
                    ).name
                    or line.product_id.seller_ids
                    and line.product_id.seller_ids[0]
                    .name.country_id.with_context(lang="en_US")
                    .name
                    or move.user_id.company_id.country_id.with_context(
                        lang="en_US"
                    ).name
                )
                weight = float_round(
                    line.product_id.weight * line.quantity,
                    precision_digits=precision_weight_digits,
                )
                hs_code = "MISSING"
                if line.product_id.intrastat_code_id:
                    hs_code = line.product_id.intrastat_code_id.name
                intrastat_text = f"\nHS CODE: {hs_code} "
                if hs_code not in intrastat_info:
                    intrastat_info[hs_code] = {"weight": 0, "price_subtotal": 0}
                intrastat_text += f"COUNTRY OF ORIGIN: {country_name} "
                intrastat_info[hs_code]["weight"] += weight
                weight = lang.format(
                    f"%.{precision_weight_digits or 2}f",
                    weight,
                    grouping=True,
                    monetary=False,
                )
                intrastat_text += f"NET WEIGHT: {weight} kg"
                intrastat_info[hs_code]["price_subtotal"] += line.price_subtotal
                if "HS CODE" in line.name:
                    line.name = re.compile("\nHS CODE.*").sub("", line.name)
                line.name += intrastat_text
            if "HS Codes:" in move.narration:
                move.narration = re.compile("\nHS Codes:.*").sub("", move.narration)
                move.narration = re.compile("\n[0-9]{4,12}: .*€").sub(
                    "", move.narration
                )
            move.narration += "\nHS Codes:\n"
            intrastat_info = {
                x: {
                    "weight": lang.format(
                        f"%.{precision_weight_digits or 2}f",
                        intrastat_info[x]["weight"],
                        grouping=True,
                        monetary=False,
                    ),
                    "price_subtotal": lang.format(
                        "%.2f",
                        intrastat_info[x]["price_subtotal"],
                        grouping=True,
                        monetary=True,
                    ),
                }
                for x in intrastat_info
            }
            move.narration += "\n".join(
                [
                    f"{n}: {intrastat_info[n]['weight']} kg |"
                    f" {intrastat_info[n]['price_subtotal']} €"
                    for n in intrastat_info
                ]
            )

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
