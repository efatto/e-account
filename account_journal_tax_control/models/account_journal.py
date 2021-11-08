# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    account_tax_control_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='account_journal_tax_rel',
        column1='journal_id',
        column2='tax_id',
        string='Tax',
    )