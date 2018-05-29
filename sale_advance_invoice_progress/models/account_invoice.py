# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    advance_invoice_id = fields.Many2one('account.invoice', 'Advance invoice')
