# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_partner_product_additional_description(self):
        for move in self:
            if move.partner_id.parent_id:
                move.partner_product_additional_description_id = \
                    move.partner_id.parent_id.\
                    partner_product_additional_description_id
            else:
                move.partner_product_additional_description_id = \
                    move.partner_id.\
                    partner_product_additional_description_id

    partner_product_additional_description_id = fields.Many2one(
        comodel_name='product.additional.description',
        compute=get_partner_product_additional_description,
        string='Product additional description',
        help='This description will be added to all product moved with this '
             'partner',
    )
