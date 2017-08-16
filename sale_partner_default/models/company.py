# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_partner_default = fields.Many2one(
        comodel_name='res.partner',
        company_dependent=True,
        help='Default sale partner for many conditions, as pricelist, '
             'discount, term of payment, etc.')
