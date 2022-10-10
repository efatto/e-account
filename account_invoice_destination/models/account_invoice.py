# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    address_destination_id = fields.Many2one(
        comodel_name="res.partner",
        string='TRANSIT WAREHOUSE',
        help="Optional destination for extra CEE.")
