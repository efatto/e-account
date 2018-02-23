# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    discount = fields.Float()

    @api.multi
    @api.depends('fiscal_position', 'discount', 'invoice_line')
    def invoice_discount_update(self):
        for invoice in self:
            for line in invoice.invoice_line:
                if line.product_id.type != 'service':
                    line.discount = invoice.discount
