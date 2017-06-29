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
                lambda x: x.invoice_state != 'invoiced'
            ) else True
            order.picking_done = False if order.picking_ids.filtered(
                lambda x: x.state != 'done'
            ) else True
            # amount = 0.0
            # amount += sum(order.picking_ids.filtered(
            #     lambda x: x.invoice_state == 'invoiced'
            # )).amount_total
            # order.amount_invoiced = amount


    # amount_invoiced = fields.Float(
    #     compute=_get_invoiced_amount_on_picking)
    picking_invoiced = fields.Boolean(
        compute=_get_picking_state)
    picking_done = fields.Boolean(
        compute=_get_picking_state)
