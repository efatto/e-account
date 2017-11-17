# -*- coding: utf-8 -*-
##############################################################################
# Author Vincent Renaville. Copyright 2015 Camptocamp SA
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def test_invoice_line_tax(self):
        res = super(AccountInvoice, self).test_invoice_line_tax()
        errors = []
        error_template = _("Invoice has line %s with tax not admitted")
        for invoice in self:
            for invoice_line in invoice.invoice_line:
                if invoice_line.invoice_line_tax_id not in invoice.journal_id.\
                        account_tax_control_ids:
                    error_string = error_template % invoice_line.name
                    errors.append(error_string)
        if errors:
            errors_full_string = ','.join(x for x in errors)
            raise exceptions.Warning(_('Invalid Journal Taxes!'),
                                     errors_full_string)
        return res
