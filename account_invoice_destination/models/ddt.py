# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class StockPickingPackagePreparation(models.Model):
    _inherit = "stock.picking.package.preparation"

    address_destination_id = fields.Many2one(
        comodel_name="res.partner",
        string='TRANSIT WAREHOUSE',
        help="Optional destination for extra CEE.")
