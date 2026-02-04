import json
import logging
import re
from urllib.parse import urljoin

import requests

from odoo import _, models
from odoo.exceptions import UserError

from .check_order_mixin import check_attachment

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "check.order.mixin.parent"]

    def button_check_attachment(self):
        self.ensure_one()
        check_attachment(self, self.order_line)

    def _n8n_webhook(self, option=False, data=False, extracted_text=False):
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        env_running = ""
        if "test" in base_url:
            env_running = "-test"
        # TODO put here the most of the logic, then call n8n or directly an ai only when
        #  needed
        # TODO add authentication? with n8n user and password
        # headers = {
        #     "Accepts": "application/json",
        #     # "X-CMC_PRO_API_KEY": API_KEY,
        # }
        if option == "read_attach":
            odoo_webhook = urljoin(
                base_url, f"/n8n/webhook{env_running}/read-attachment"
            )
            params = {"sale_order_id": self.id}
            try:
                req = requests.post(
                    url=odoo_webhook,
                    data=params,
                    timeout=30,
                    # headers=headers,
                    verify=False,
                )
                response = req.json()
            except IOError as e:
                error_msg = _("Something went wrong during data submission: %s") % e
                raise UserError(error_msg)
        else:
            odoo_webhook = urljoin(
                base_url, f"/n8n/webhook{env_running}/insert-so-rows"
            )
            params = {
                "sale_order_id": self.id,
                "data": json.dumps(data),
                "extracted_text": extracted_text,
            }
            try:
                # response = requests.post(
                #     urljoin(params.api_url,
                #     "/v3/domains/%s/webhooks" % params.domain),
                #     auth=("api", params.api_key),
                #     data={"id": event, "url": [odoo_webhook]},
                # )
                req = requests.get(
                    url=odoo_webhook,
                    params=params,
                    timeout=30,
                    # headers=headers,
                    verify=False,
                )
                response = req.json()
            except IOError as e:
                error_msg = _("Something went wrong during data submission: %s") % e
                raise UserError(error_msg)
        return response

    def _get_products_from_content(self, content) -> list:
        product_codes = self.env["product.product"].search_read(
            [
                ("default_code", "!=", False),
            ],
            ["default_code"],
        )
        found_product_codes = []
        for product_code in product_codes:
            if (
                len(product_code["default_code"]) > 2
                and product_code["default_code"] in content
            ):
                found_product_codes.append(product_code)
        customer_product_codes = self.env["product.customerinfo"].search_read(
            ["|", ("product_code", "!=", False), ("product_name", "!=", False)],
            ["product_code", "product_name", "product_id", "product_tmpl_id"],
        )
        if customer_product_codes:
            for customer_product_code in customer_product_codes:
                if (
                    customer_product_code.get("product_code")
                    and len(customer_product_code["product_code"]) > 2
                    and customer_product_code["product_code"] in content
                    or customer_product_code.get("product_name")
                    and len(customer_product_code["product_name"]) > 2
                    and customer_product_code["product_name"] in content
                ):
                    # escludes products already in product_codes
                    product = False
                    if customer_product_code.get("product_id"):
                        product_id = customer_product_code["product_id"]
                        product = self.env["product.product"].browse(product_id)
                    elif customer_product_code.get("product_tmpl_id"):
                        product = self.env["product.product"].search(
                            [
                                (
                                    "product_tmpl_id",
                                    "=",
                                    customer_product_code["product_tmpl_id"][0],
                                )
                            ],
                            limit=1,
                        )
                    if product and product.default_code not in [
                        x["default_code"] for x in found_product_codes
                    ]:
                        found_product_codes.append(
                            {
                                "default_code": product.default_code,
                                "id": product.id,
                            }
                        )
        return found_product_codes

    @staticmethod
    def _convert_string_to_float(string_value):
        converted_string_value = 0
        r = re.search(r'(\d+)[.,](\d+)[.,]?(\d*)', string_value)
        if r:
            if r.group(3):
                converted_string_value = '{0}{1}.{2}'.format(*r.groups())
            elif r.group(2):
                converted_string_value = '{0}.{1}'.format(*r.groups())
            else:
                converted_string_value = '{}'.format(*r.groups())
        try:
            converted_string_value = float(converted_string_value)
        except ValueError:
            pass
        return converted_string_value

    def _create_order_lines(self, values_dict):
        current_so_lines = self.order_line
        logger.info(f"N8N connector: importing from n8n values_dict: {values_dict}")
        if isinstance(values_dict, dict):
            if values_dict.get("order_id") and values_dict.get("order_lines"):
                sale_order = self.env["sale.order"].search(
                    [
                        ("id", "=", values_dict["order_id"]),
                    ]
                )
                for values in values_dict.get("order_lines"):
                    if values.get("product_id"):
                        product = self.env["product.product"].search(
                            [
                                ("id", "=", values["product_id"]),
                            ]
                        )
                        if product:
                            price_unit = self._convert_string_to_float(
                                values.get("price_unit", 0))
                            product_uom_qty = self._convert_string_to_float(
                                values.get("quantity", 0))
                            sale_order.write(
                                {
                                    "order_line": [
                                        (
                                            0,
                                            0,
                                            {
                                                "product_id": product.id,
                                                "price_unit": price_unit,
                                                "product_uom_qty": product_uom_qty,
                                            },
                                        )
                                    ],
                                }
                            )
        contents = ""
        if self.order_line != current_so_lines:
            contents = "\n".join(
                [line.name for line in self.order_line - current_so_lines]
            )
        if contents:
            logger.info(f"N8N connector: imported lines with products: {contents}")
        else:
            logger.info("N8N connector: no new lines were imported.")

    def button_create_row_from_attachment(self):
        self.ensure_one()
        response = self._n8n_webhook(option="read_attach")
        extracted_text = response.get("extractedText")
        if extracted_text:
            products = self._get_products_from_content(extracted_text)
            if products:
                # call n8n to create the sale order lines with the found products
                res = self._n8n_webhook(data=products, extracted_text=extracted_text)
                if not res:
                    raise UserError(_("No sale order lines were created."))
                else:
                    self._create_order_lines(res)
        else:
            raise UserError(_("No extracted text received."))
