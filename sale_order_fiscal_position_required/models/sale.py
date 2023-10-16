# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        if any(self.filtered(lambda so: not so.fiscal_position_id)):
            raise ValidationError(_("Missing fiscal position!"))
        res = super().action_confirm()
        return res
