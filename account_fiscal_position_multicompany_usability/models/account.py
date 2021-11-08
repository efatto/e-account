# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountFiscalPositionTax(models.Model):
    _inherit = 'account.fiscal.position.tax'

    tax_src_company_id = fields.Many2one(
        related='tax_src_id.company_id')
    tax_dest_company_id = fields.Many2one(
        related='tax_dest_id.company_id')
