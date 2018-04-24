# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    default_sale_discount = fields.Float(
        string="Default sales discount (%)",
        company_dependent=True)
    default_sale_complex_discount = fields.Char(
        'Complex Discount',
        size=32,
        company_dependent=True,
        help='E.g.: 15.5+5, or 50+10+3.5')