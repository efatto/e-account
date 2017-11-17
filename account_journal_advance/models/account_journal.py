# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    advance_description = fields.Char(
        string='Description for advance documents',
        size=64, translate=True,
    )