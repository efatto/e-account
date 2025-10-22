import os

from odoo import _, models, fields
from odoo import _, tools
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
from .check_order_confirm import check_code_and_qty


def check_attachment(object_to_check, object_to_check_lines):
    object_to_check.ensure_one()
    if not object_to_check.attachment_to_check_id:
        raise ValidationError(_("No attachment found to check"))
    lines_to_check = object_to_check_lines.filtered(
        lambda x: x.product_id.type == "product" and x.product_id.default_code
    )
    filestore = tools.config.filestore(object_to_check._cr.dbname)
    file_path = os.path.join(filestore, object_to_check.attachment_to_check_id.store_fname)
    file_ext = object_to_check.attachment_to_check_id.mimetype.replace("application/", "")
    _logger.info(
        f"Checking file {file_path} with extension {file_ext} for sale order "
        f"{object_to_check.name}"
    )
    target_results = check_code_and_qty(
        file_path,
        file_ext,
        {
            line.product_id.default_code: int(line.product_uom_qty)
            for line in lines_to_check
        },
    )
    for line in lines_to_check:
        target_result = target_results.get(line.product_id.default_code)
        if not target_result or target_result[0] == "Undefined":
            check_result = False
            check_message = _("No result found for this line")
        else:
            check_result = target_result[0]
            check_message = target_result[1]
        line.check_result = check_result
        line.check_message = check_message
    if all(x.check_result for x in lines_to_check):
        object_to_check.check_result = True
        object_to_check.check_message = _("All lines checked")


class CheckOrderMixinChild(models.AbstractModel):
    _name = "check.order.mixin.child"
    _description = "Check Order Mixin"

    check_result = fields.Boolean(
        string="Confirmation check result",
        default=False,
    )
    check_message = fields.Char(
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
