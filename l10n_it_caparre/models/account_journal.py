# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    caparre = fields.Boolean()
