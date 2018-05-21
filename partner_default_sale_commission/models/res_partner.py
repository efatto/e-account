# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_sale_commission_id = fields.Many2one(
        comodel_name="sale.commission",
        string="Default commission")
