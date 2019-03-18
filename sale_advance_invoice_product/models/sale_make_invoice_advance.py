# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def onchange_method(self, advance_payment_method, product_id):
        if advance_payment_method == 'percentage':
            return {'value': {'amount': 0}}
        return super(SaleAdvancePaymentInv, self).onchange_method(
            advance_payment_method, product_id
        )
