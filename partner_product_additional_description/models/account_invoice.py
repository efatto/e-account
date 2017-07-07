# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice'

    partner_product_additional_description = fields.Many2one(
        related='partner_id.partner_product_additional_description'
    )
