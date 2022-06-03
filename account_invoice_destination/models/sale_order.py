# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    address_destination_id = fields.Many2one(
        comodel_name="res.partner",
        string='Final Destination',
        help="Optional destination for extra CEE.")
