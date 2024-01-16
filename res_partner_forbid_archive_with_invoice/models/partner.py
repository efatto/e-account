# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="partner_id",
        string="Move Lines",
    )

    def toggle_active(self):
        if any(
            x.invoice_ids or x.move_line_ids for x in self.filtered(lambda x: x.active)
        ):
            raise UserError(
                _(
                    "Some selected partner has registered invoices or moves! \n"
                    "You cannot deactivate these partners: %s"
                )
                % (" - ".join(self.mapped("name")))
            )
        super().toggle_active()
