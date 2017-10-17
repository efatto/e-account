# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    caparre = fields.Boolean()


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    caparra = fields.Boolean(related='journal_id.caparre')
