# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.depends('fiscal_document_type_id')
    def _compute_is_advance_invoice(self):
        for invoice in self:
            if invoice.fiscal_document_type_id.code in ['TD02', 'TD03']:
                invoice.is_advance_invoice = True

    is_advance_invoice = fields.Boolean(
        compute=_compute_is_advance_invoice,
        string="Advance invoice")
