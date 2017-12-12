# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    stock_picking_package_preparation_ids = fields.One2many(
        'stock.picking.package.preparation', 'invoice_id', 'Pickings',
        groups="stock.group_stock_user", readonly=True)