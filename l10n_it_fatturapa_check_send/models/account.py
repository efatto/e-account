# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountPeriod(models.Model):
    _inherit = "account.period"

    disable_send_foreign_invoice = fields.Boolean(default=True)
