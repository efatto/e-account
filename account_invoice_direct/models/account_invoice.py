# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    direct_invoice = fields.Boolean()
