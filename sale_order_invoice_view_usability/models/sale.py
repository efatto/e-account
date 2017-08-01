# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_picking_state(self):
        for order in self:
            order.picking_invoiced = False if order.picking_ids.filtered(
                lambda x: x.invoice_state != 'invoiced' and x.state != 'cancel'
            ) else True
            order.picking_done = False if order.picking_ids.filtered(
                lambda x: x.state not in ['cancel', 'done']
            ) else True

    picking_invoiced = fields.Boolean(
        compute=_get_picking_state)
    picking_done = fields.Boolean(
        compute=_get_picking_state)
