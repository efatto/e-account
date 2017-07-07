# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight = fields.Float(
        compute='_compute_weight',
        help="The weight is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume = fields.Float(
        compute='_compute_weight',
        help="The volume is computed when the invoice is done.",
        digits_compute=dp.get_precision('Stock Weight'))
    weight_custom = fields.Float(
        help="Put here weight when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'))
    net_weight_custom = fields.Float(
        help="Put here net weight when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'))
    volume_custom = fields.Float(
        help="Put here net volume when computed amount is not exact.",
        digits_compute=dp.get_precision('Stock Weight'))
    compute_weight = fields.Boolean(default=True)

    @api.multi
    def _compute_weight(self):
        for invoice in self:
            #todo for sale in invoice.sale_id ?? if in the order-picking was set a custom weight
            if invoice.compute_weight:
                invoice.net_weight = sum(
                    l.product_id.weight_net and l.product_id.weight_net
                    * l.quantity for l in invoice.invoice_line)
                invoice.weight = sum(
                    l.product_id.weight and l.product_id.weight
                    * l.quantity for l in invoice.invoice_line)
                invoice.volume = sum(
                    l.product_id.volume and l.product_id.volume
                    * l.quantity for l in invoice.invoice_line)
            else:
                invoice.net_weight = invoice.net_weight_custom
                invoice.weight = invoice.weight_custom
                invoice.volume = invoice.volume_custom
