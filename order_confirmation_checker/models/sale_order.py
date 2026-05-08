import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

from .check_order_mixin import check_attachment, convert_string_to_float

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "check.order.mixin.parent"]

    def button_check_attachment(self):
        self.ensure_one()
        check_attachment(self, self.order_line)

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

    def _create_order_lines(self, values_dict):
        current_so_lines = self.order_line
        logger.info(f"N8N connector: importing from n8n values_dict: {values_dict}")
        if isinstance(values_dict, dict):
            if values_dict.get("orders"):
                orders = values_dict["orders"]
                for order in orders:
                    if order.get("order_id") and order.get("order_lines"):
                        assert self.id == int(order.get("order_id"))
                        sale_order = self
                        if order.get("delivery_date"):
                            sale_order.commitment_date = fields.Date.from_string(
                                order.get("delivery_date")
                            )
                        if order != orders[0]:
                            sale_order = self.copy(
                                default={
                                    "order_line": False,
                                    "commitment_date": fields.Date.from_string(
                                        order.get("delivery_date")
                                    )
                                    if order.get("delivery_date")
                                    else None,
                                }
                            )
                        for values in order.get("order_lines"):
                            if values.get("product_id") and values.get("quantity"):
                                product = self.env["product.product"].search(
                                    [
                                        ("id", "=", values["product_id"]),
                                    ]
                                )
                                if product:
                                    product_qty = convert_string_to_float(
                                        values.get("quantity", 0)
                                    )
                                    sale_order.write(
                                        {
                                            "order_line": [
                                                (
                                                    0,
                                                    0,
                                                    {
                                                        "product_id": product.id,
                                                        "product_uom_qty": product_qty,
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
