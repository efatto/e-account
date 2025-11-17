from odoo import models
from odoo.tools import float_round, get_lang


class GetIntrastatInfo(models.AbstractModel):
    _name = "get.intrastat.info"
    _description = "Get Intrastat Info"

    def _get_info(
        self, product_id, quantity, price_subtotal, intrastat_info=None,
    ):
        # if the country of origin is not found in the product, get it from the first
        # seller of the product and eventually from the current company
        lang = get_lang(self.env, lang_code=self.env.company.partner_id.lang)
        precision_weight_digits = (
            self.env["decimal.precision"].search([("name", "=", "Stock Weight")]).digits
        )
        country_name = (
            product_id.intrastat_country_origin_id
            and product_id.intrastat_country_origin_id.with_context(
            lang="en_US"
        ).name
            or product_id.seller_ids
            and product_id.seller_ids[0]
            .name.country_id.with_context(lang="en_US")
            .name
            or self.env.user.company_id.country_id.with_context(
            lang="en_US"
        ).name
        )
        weight = float_round(
            product_id.weight * quantity,
            precision_digits=precision_weight_digits,
        )
        hs_code = "MISSING"
        if product_id.intrastat_code_id:
            hs_code = product_id.intrastat_code_id.name
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
        intrastat_info[hs_code]["price_subtotal"] += price_subtotal
        return intrastat_text, intrastat_info

    def _get_narration(self, intrastat_info=None):
        lang = get_lang(self.env, lang_code=self.env.company.partner_id.lang)
        precision_weight_digits = (
            self.env["decimal.precision"].search([("name", "=", "Stock Weight")]).digits
        )
        narration = "\nHS Codes:\n"
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
        narration += "\n".join(
            [
                f"{n}: {intrastat_info[n]['weight']} kg |"
                f" {intrastat_info[n]['price_subtotal']} €"
                for n in intrastat_info
            ]
        )
        return narration
