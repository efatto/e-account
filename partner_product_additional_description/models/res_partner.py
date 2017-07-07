# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductAdditionalDescription(models.Model):
    _name = 'product.additional.description'
    _description = 'Additional description for product from partner'

    name = fields.Char('Additional description')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_product_additional_description = fields.Many2one(
        comodel_name='product.additional.description',
        string='Additional description',
    )
