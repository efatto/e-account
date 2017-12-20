# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    downpayment = fields.Boolean()
