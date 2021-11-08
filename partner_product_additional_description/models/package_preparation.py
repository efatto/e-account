# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class StockPickingPackagePreparation(models.Model):
    _inherit = 'stock.picking.package.preparation'

    def get_partner_product_additional_description(self):
        for pack in self:
            if pack.partner_id.parent_id:
                pack.partner_product_additional_description_id = \
                    pack.partner_id.parent_id.\
                    partner_product_additional_description_id
            else:
                pack.partner_product_additional_description_id = \
                    pack.partner_id.\
                    partner_product_additional_description_id

    partner_product_additional_description_id = fields.Many2one(
        comodel_name='product.additional.description',
        compute=get_partner_product_additional_description,
        string='Product additional description',
        help='This description will be added to all product moved with this '
             'partner',
    )
