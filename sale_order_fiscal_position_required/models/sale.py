# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_fiscal_position_required = fields.Boolean(
        string='Is Fiscal Position Required',
        default=True,
    )

    @api.multi
    def action_confirm(self):
        if not config["test_enable"]:
            if any(
                self.filtered(
                    lambda so: so.is_fiscal_position_required
                    and not so.fiscal_position_id
                )
            ):
                raise ValidationError(_("Missing fiscal position in sale order!"))
        res = super().action_confirm()
        return res
