# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_type = fields.Selection([
        ('transport', 'Transport'),
        ('other', 'Other'),
        ('contribution', 'Fixed Costs'),
        ('discount', 'Discount'),
    ], string='Service type')