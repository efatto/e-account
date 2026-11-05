from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountFiscalPosition(models.Model):
    _name = "account.fiscal.position"
    _inherit = ["account.fiscal.position", "mail.thread"]


class AccountFiscalPositionTax(models.Model):
    _inherit = "account.fiscal.position.tax"

    @api.constrains("tax_src_id", "tax_dest_id")
    def _check_tax_mapping(self):
        for tax_mapping in self:
            if tax_mapping.tax_src_id == tax_mapping.tax_dest_id:
                raise ValidationError(
                    _("Taxes source and destination must be different.")
                )
            if (
                tax_mapping.tax_src_id.type_tax_use
                != tax_mapping.tax_dest_id.type_tax_use
            ):
                raise ValidationError(
                    _(
                        "Taxes source and destination must have the same type of tax "
                        "use."
                    )
                )
