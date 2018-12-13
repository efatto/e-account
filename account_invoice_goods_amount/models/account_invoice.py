# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_goods_amount = fields.Float(
        compute='_compute_goods_amount',
        string='Goods and service amount',
        help='This amount exclude invoice line without product or with '
             'downpayment product type.')

    @api.multi
    def _compute_goods_amount(self):
        for invoice in self:
            total = 0
            for line in invoice.invoice_line:
                if line.product_id:
                    if not line.product_id.downpayment:
                        total += line.price_subtotal
            self.invoice_goods_amount = total
