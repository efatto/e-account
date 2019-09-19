# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_advance_invoice = fields.Boolean(string="Advance invoice")
