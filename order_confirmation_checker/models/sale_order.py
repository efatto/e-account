import json
import logging
import re
from string import Template

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.ai_tool.tools import aitool

from .check_order_confirm import extract_text
from .check_order_mixin import (
    check_attachment,
    convert_string_to_float,
    get_attachment_file,
)

logger = logging.getLogger(__name__)

ORDER_LINES_PROMPT = """You are a sale manager creating one or more sale orders from
a document received from a customer. The document usually contains our company name
($company_name), the customer name, the document date and a list of ordered products.

Return only a single valid JSON object, without markdown fences or comments, with the
following structure:
{
  "company_id": $company_id,
  "customer": "customer name",
  "order_date": "YYYY-MM-DD",
  "client_order_ref": "customer order reference",
  "orders": [
    {
      "order_id": $order_id,
      "delivery_date": "YYYY-MM-DD",
      "elaboration_notes": "notes about the extraction",
      "order_lines": [
        {
          "product_code": "code as it appears in the customer document",
          "partner_product_name": "description as it appears in the document",
          "product_id": 0,
          "quantity": 0,
          "price_unit": 0
        }
      ]
    }
  ]
}

INSTRUCTIONS:
1. company_id: MANDATORY, use exactly $company_id.
2. customer: find the customer in the document. It is a company name different from
   our company name, usually in the header, footer or upper left position. Ignore the
   delivery company usually placed before the footer.
3. order_date: find the order date in the document, usually in the header or in the
   upper position of the first page, before the product rows. If there are different
   dates, the order date is usually today or a few days before today, while a future
   date is usually the requested delivery date. Use the YYYY-MM-DD format.
4. client_order_ref: find the customer order reference (for example their PO number).
5. orders: find the delivery date requested for the products. If there is only one
   delivery date valid for the whole order, create a single order containing all the
   rows. If there are many delivery dates, one per row, group the rows by delivery
   date and create one order per delivery date.
6. order_id: MANDATORY, use exactly $order_id.
7. delivery_date: use the delivery date found in the document, in YYYY-MM-DD format.

CRITICAL PRODUCT IDENTIFICATION RULES:
Use only the list of available products provided below in "PRODUCTS".
Each element is a dictionary with "id" (the Odoo product id), "default_code" (our
internal product code) and optionally "customer_code" (the customer specific code).
For every row in the document table:
a. Extract the product code or description from the document.
b. Search it in PRODUCTS and match it with either "default_code" or "customer_code".
   The list is sorted from the most complex/longest code to the simplest one: stop at
   the very first match, so a specific code is preferred over a simpler one contained
   in it.
c. If a match is found, use the corresponding integer "id" from PRODUCTS.
d. Do not invent product ids and do not use the product code as the id.
e. If no product matches a row, skip that row or set product_id to null.

Each order line must contain:
- product_id: the integer "id" found in PRODUCTS, or null when not matched.
- quantity: the requested quantity as a number.
- price_unit: the requested unit price as a number.
- product_code: the code as it appears in the customer document.
- partner_product_name: the description as it appears in the customer document.

PRODUCTS:
$products

DOCUMENT TEXT:
$extracted_text
"""


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "check.order.mixin.parent"]

    def button_check_attachment(self):
        self.ensure_one()
        check_attachment(self, self.order_line)

    def button_create_row_from_attachment(self):
        self.ensure_one()
        tool = self.env.ref(
            "order_confirmation_checker.ai_tool_create_order_lines_from_attachment"
        )
        tool._execute_tool(record=self)

    @aitool(
        input_schema={},
        output_schema={
            "text": {"type": "string"},
        },
    )
    def _ai_extract_attachment_text(self):
        self.ensure_one()
        attachment = self.attachment_to_check_id
        if not attachment:
            raise UserError(_("No attachment found to check"))
        file_path, file_ext = get_attachment_file(attachment)
        return {"text": extract_text(file_path, file_ext)}

    @aitool(
        input_schema={},
        output_schema={
            "order_ids": {
                "type": "array",
                "items": {"type": "integer"},
            },
        },
    )
    def _ai_create_order_lines_from_attachment(self):
        self.ensure_one()
        extracted_text = self._ai_extract_attachment_text().get("text")
        if not extracted_text:
            raise UserError(_("No extracted text received."))
        products = self._get_products_from_content(extracted_text)
        if not products:
            raise UserError(_("No products found in the attachment."))
        prompt = self._prepare_order_lines_prompt(extracted_text, products)
        response = self._get_ai_connection()._run(prompt=prompt)
        values_dict = self._parse_ai_order_lines(response[0] if response else "")
        if not values_dict:
            raise UserError(_("No sale order lines were created."))
        sale_orders = self._create_order_lines(values_dict)
        if not sale_orders.order_line:
            raise UserError(_("No sale order lines were created."))
        return {"order_ids": sale_orders.ids}

    def _prepare_order_lines_prompt(self, extracted_text, products):
        self.ensure_one()
        return Template(ORDER_LINES_PROMPT).substitute(
            company_id=self.env.company.id,
            company_name=self.env.company.name,
            order_id=self.id,
            products=json.dumps(products, indent=2, ensure_ascii=False),
            extracted_text=extracted_text,
        )

    @staticmethod
    def _parse_ai_order_lines(content):
        """Extract the JSON object from the AI response."""
        if isinstance(content, dict):
            return content
        if not content:
            return {}
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return {}
        try:
            result = json.loads(match.group(0))
        except ValueError:
            logger.info("Invalid JSON returned by the AI connection: %s", content)
            return {}
        return result if isinstance(result, dict) else {}

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
                product_code["customer_code"] = ""
                found_product_codes.append(product_code)
        customer_product_codes = self.env["product.customerinfo"].search_read(
            [
                ("partner_id", "=", self.partner_id.id),
                "|",
                ("product_code", "!=", False),
                ("product_name", "!=", False),
            ],
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
                        product_template = self.env["product.template"].browse(
                            customer_product_code["product_tmpl_id"][0],
                        )
                        product = product_template.product_variant_id
                    if product and product.default_code not in [
                        x["default_code"] for x in found_product_codes
                    ]:
                        found_product_codes.append(
                            {
                                "default_code": product.default_code,
                                "id": product.id,
                                "customer_code": customer_product_code.get(
                                    "product_code"
                                ),
                            }
                        )
        # sort by length of codes to help AI matching (complex to simple)
        found_product_codes.sort(
            key=lambda x: max(
                len(x.get("default_code") or ""), len(x.get("customer_code") or "")
            ),
            reverse=True,
        )
        return found_product_codes

    def _create_order_lines(self, values_dict):  # noqa: C901
        current_so_lines = self.order_line
        sale_orders = self
        logger.info("AI connector: importing order values_dict: %s", values_dict)
        if isinstance(values_dict, dict):
            order_date = False
            client_order_ref = False
            if values_dict.get("order_date"):
                try:
                    order_date = fields.Date.from_string(values_dict["order_date"])
                except ValueError:
                    order_date = False
            if values_dict.get("client_order_ref"):
                client_order_ref = values_dict["client_order_ref"]
            if values_dict.get("orders"):
                orders = values_dict["orders"]
                for order in orders:
                    if order.get("order_id") and order.get("order_lines"):
                        assert self.id == int(order.get("order_id"))
                        sale_order = self
                        if order_date:
                            sale_order.date_order = order_date
                        if client_order_ref:
                            sale_order.client_order_ref = client_order_ref
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
                            sale_orders |= sale_order
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
            logger.info("AI connector: imported lines with products: %s", contents)
        else:
            logger.info("AI connector: no new lines were imported.")
        return sale_orders
