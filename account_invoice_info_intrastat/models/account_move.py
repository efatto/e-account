import re

from odoo import models
from odoo.tools import float_round, get_lang


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_insert_intrastat_data_in_move_lines(self):
        precision_weight_digits = (
            self.env["decimal.precision"].search([("name", "=", "Stock Weight")]).digits
        )
        for move in self.filtered(lambda x: x.move_type.startswith("out_")):
            for line in move.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.type != "service"
            ):
                # if country of origin is not found in product,
                # get it from first seller of the product, in the last chance from
                # the current company
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
                intrastat_text += f"COUNTRY OF ORIGIN: {country_name} "
                lang = get_lang(self.env, lang_code=self.env.company.partner_id.lang)
                amount = lang.format(
                    "%.2f", line.price_subtotal, grouping=True, monetary=True
                )
                weight = lang.format(
                    f"%.{precision_weight_digits or 2}f",
                    weight,
                    grouping=True,
                    monetary=False,
                )
                intrastat_text += f"NET WEIGHT: {weight} kg AMOUNT: € {amount}"
                if "HS CODE" in line.name:
                    line.name = re.compile("\nHS CODE.*").sub("", line.name)
                line.name += intrastat_text

    def action_remove_intrastat_data_in_move_lines(self):
        for move in self.filtered(lambda x: x.move_type.startswith("out_")):
            for line in move.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.type != "service"
            ):
                if "HS CODE" in line.name:
                    line.name = re.compile("\nHS CODE.*").sub("", line.name)
