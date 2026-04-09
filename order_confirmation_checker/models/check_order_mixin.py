import logging
import os
import re

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError

from .check_order_confirm import check_code_and_qty

_logger = logging.getLogger(__name__)


def check_attachment(object_to_check, object_to_check_lines):
    object_to_check.ensure_one()
    if not object_to_check.attachment_to_check_id:
        raise ValidationError(_("No attachment found to check"))
    lines_to_check = object_to_check_lines.filtered(
        lambda x: x.product_id.type == "product" and x.product_id.default_code
    )
    filestore = tools.config.filestore(object_to_check._cr.dbname)
    file_path = os.path.join(
        filestore, object_to_check.attachment_to_check_id.store_fname
    )
    file_ext = object_to_check.attachment_to_check_id.mimetype.replace(
        "application/", ""
    )
    lang = tools.get_lang(
        object_to_check.env, lang_code=object_to_check.partner_id.lang
    )
    _logger.info(
        f"Checking file {file_path} with extension {file_ext} for sale order "
        f"{object_to_check.name}"
    )
    data_to_check = {}
    for line in lines_to_check:
        partner_code = False
        if line._name == "purchase.order.line":
            partner = (
                line.partner_id
                if not line.partner_id.parent_id
                else line.partner_id.parent_id
            )
            if partner in line.product_id.seller_ids.mapped("name"):
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                )
                if seller:
                    partner_code = seller[0].product_code or ""
        elif line._name == "sale.order.line":
            if line.product_id and line.order_id and line.order_id.partner_id:
                customer = line.product_id._select_customerinfo(
                    partner=line.order_partner_id,
                    quantity=None,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                )
                if customer:
                    partner_code = customer[0].product_code or ""
        data_to_check[line.id] = dict(
            default_code=line.product_id.default_code,
            quantity=lang.format(
                "%.0f",
                line.product_uom_qty,
                grouping=True,
                monetary=False,
            ),
            partner_code=partner_code or "",
            price_total=lang.format(
                "%.0f",
                line.price_subtotal,
                grouping=True,
                monetary=False,
            ),
        )
    target_results = check_code_and_qty(
        file_path,
        file_ext,
        data_to_check,
    )
    for line in lines_to_check:
        if target_results.get(line.id):
            target_result = target_results[line.id]
            for key in target_result:
                line.check_result = key
                line.check_message = target_result[key]
        else:
            line.check_result = False
            line.check_message = _("No match found")
    if all(x.check_result for x in lines_to_check):
        object_to_check.check_result = True
        object_to_check.check_message = _("All lines checked")


@staticmethod
def _convert_string_to_float(string_value):
    r = re.search(r"(\d+)[.,](\d+)[.,]?(\d*)", string_value)
    if r:
        if r.group(3):
            converted_string_value = "{}{}.{}".format(*r.groups())
        elif r.group(2):
            converted_string_value = "{}.{}".format(*r.groups())
        else:
            converted_string_value = "{}".format(*r.groups())
    else:
        converted_string_value = string_value
    try:
        converted_string_value = float(converted_string_value)
    except ValueError:
        pass
    return converted_string_value


class CheckOrderMixinChild(models.AbstractModel):
    _name = "check.order.mixin.child"
    _description = "Check Order Mixin"

    check_result = fields.Boolean(
        string="Confirmation check result",
        default=False,
    )
    check_message = fields.Text(
        string="Confirmation check message",
    )


class CheckOrderMixinParent(models.AbstractModel):
    _name = "check.order.mixin.parent"
    _inherit = ["check.order.mixin.child"]
    _description = "Check Order Mixin"

    attachment_to_check_id = fields.Many2one(
        comodel_name="ir.attachment",
        help="Select the attachment which contains the order confirmation",
    )
