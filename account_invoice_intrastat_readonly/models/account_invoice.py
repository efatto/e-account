from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.onchange("intrastat")
    def onchange_instrastat(self):
        if (
            self.move_type.startswith("out_")
            and self.fiscal_position_id.intrastat_sale != self.intrastat
            or self.move_type.startswith("in_")
            and self.fiscal_position_id.intrastat_purchase != self.intrastat
        ):
            raise ValidationError(
                _(
                    "Intrastat is linked from fiscal position!\n"
                    "Change fiscal position to set it."
                )
            )
