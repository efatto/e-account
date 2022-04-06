# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if not order.analytic_account_id:
            order._create_analytic_account()
        if not order.procurement_group_id:
            group_id = self.env['procurement.group'].create({
                'name': order.name,
                'move_type': order.picking_policy,
                'sale_id': order.id,
                'partner_id': order.partner_shipping_id.id,
            })
            order.procurement_group_id = group_id
        return order
