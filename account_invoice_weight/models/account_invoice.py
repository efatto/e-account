# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    weight_invoice = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
    net_weight_invoice = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
    volume_invoice = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Volume'),
        digits=dp.get_precision('Stock Volume'))
    weight_custom = fields.Float(
        help="Put here weight when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
    net_weight_custom = fields.Float(
        help="Put here net weight when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
    volume_custom = fields.Float(
        help="Put here net volume when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Volume'),
        digits=dp.get_precision('Stock Volume'))
    compute_weight = fields.Boolean(default=True)
    weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
    net_weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'),
        digits=dp.get_precision('Stock Weight'))
    volume = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Volume'),
        digits=dp.get_precision('Stock Volume'))

    @api.multi
    def _compute_weight(self):
        for invoice in self:
            # compute from invoice and sppp
            # sum weight for line without origin
            for line in invoice.invoice_line:
                if invoice.stock_picking_package_preparation_ids:
                    for sppp in invoice.stock_picking_package_preparation_ids:
                        for picking in sppp.picking_ids:
                            if line.origin and picking.origin and line.origin \
                                    not in picking.origin and \
                                    line.origin not in picking.name:
                                invoice.weight += line.product_id.\
                                    weight * line.quantity
                                invoice.net_weight += line.product_id. \
                                    weight_net * line.quantity
                                invoice.volume += line.product_id. \
                                    volume * line.quantity
                else: # if not pickings, sum all lines
                    invoice.weight += line.product_id. \
                                          weight * line.quantity
                    invoice.net_weight += line.product_id. \
                                              weight_net * line.quantity
                    invoice.volume += line.product_id. \
                                          volume * line.quantity
            # then sum weight from sppp (for residual lines)
            invoice.weight += sum(
                x.weight for x in
                invoice.stock_picking_package_preparation_ids)
            invoice.net_weight += sum(
                x.net_weight for x in
                invoice.stock_picking_package_preparation_ids)
            invoice.volume += sum(
                x.volume for x in
                invoice.stock_picking_package_preparation_ids)

            # then compute only from invoice without sppp
            invoice.net_weight_invoice = sum(
                l.product_id.weight_net and l.product_id.weight_net
                * l.quantity for l in invoice.invoice_line)
            invoice.weight_invoice = sum(
                l.product_id.weight and l.product_id.weight
                * l.quantity for l in invoice.invoice_line)
            invoice.volume_invoice = sum(
                l.product_id.volume and l.product_id.volume
                * l.quantity for l in invoice.invoice_line)
            if not invoice.compute_weight:
                invoice.net_weight = invoice.net_weight_custom
                invoice.weight = invoice.weight_custom
                invoice.volume = invoice.volume_custom
