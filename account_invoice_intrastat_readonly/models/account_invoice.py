from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.onchange("intrastat")
    def onchange_instrastat(self):
        if self.fiscal_position_id.intrastat != self.intrastat:
            raise ValidationError(
                _(
                    "Intrastat is linked from fiscal position!\n"
                    "Change fiscal position to set it."
                )
            )
