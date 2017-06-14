# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    country_id = fields.Many2one(
        related='partner_id.country_id'
    )

