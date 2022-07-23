# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_categ_id = fields.Many2one(related='product_id.categ_id')
