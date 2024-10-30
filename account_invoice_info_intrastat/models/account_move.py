from odoo import models
from odoo.tools import float_round


class AccountMove(models.Model):
    _inherit = "account.move"

    # todo put in narration info of origin like:
    # HS CODE: 84313100
    #
    def action_insert_intrastat_data_in_narration(self):
        country_model = self.env["res.country"]
        intrastat_code_model = self.env["report.intrastat.code"]
        precision_weight_digits = (
            self.env["decimal.precision"].search([("name", "=", "Stock Weight")]).digits
        )
        for move in self.filtered(lambda x: x.move_type.startswith("out_")):
            origin_dict = {}
            for line in move.invoice_line_ids.filtered(
                lambda x: x.product_id and x.product_id.type != "service"
            ).sorted(key="sequence2"):
                intrastat_data = line.product_id.product_tmpl_id.get_intrastat_data()
                country_name = (
                    intrastat_data.get("intrastat_country_origin_id")
                    and country_model.with_context(lang="en_US")
                    .browse(intrastat_data.get("intrastat_country_origin_id"))
                    .name
                    or line.product_id.seller_ids
                    and line.product_id.seller_ids[0]
                    .name.country_id.with_context(lang="en_US")
                    .name
                    or move.user_id.company_id.country_id.with_context(
                        lang="en_US"
                    ).name
                )
                if country_name not in origin_dict:
                    origin_dict[country_name] = {}
                if line.sequence2 not in origin_dict[country_name]:
                    origin_dict[country_name][line.sequence2] = {}
                weight = float_round(
                    line.product_id.weight * line.quantity,
                    precision_digits=precision_weight_digits,
                )
                origin_dict[country_name][line.sequence2].update(
                    {
                        "weight": weight,
                        "amount": line.price_subtotal,
                    }
                )
                if intrastat_data.get("intrastat_code_id"):
                    origin_dict[country_name][line.sequence2].update(
                        {
                            "code": intrastat_code_model.browse(
                                intrastat_data.get("intrastat_code_id")
                            ).name,
                        }
                    )
                # "intrastat_type": not used
            narration_text = "\n"
            hs_codes = {}
            for country in origin_dict:
                amount = 0
                weight = 0
                new_hs_codes = {
                    origin_dict[country][pos]["code"] for pos in origin_dict[country]
                }
                if new_hs_codes != hs_codes:
                    hs_codes = new_hs_codes
                    for hs_code in hs_codes:
                        narration_text += f"HS CODE: {hs_code}\n"
                    narration_text += "\nCOUNTRY OF ORIGIN:\n\n"
                narration_text += f"{country}:\npos. "
                narration_text += "-".join(f"{pos}" for pos in origin_dict[country])
                for pos in origin_dict[country]:
                    amount += origin_dict[country][pos]["amount"]
                    weight += origin_dict[country][pos]["weight"]
                narration_text += f"\nnet weight {weight:n} kg | " f"€ {amount:n}\n\n"
            move.narration += narration_text
