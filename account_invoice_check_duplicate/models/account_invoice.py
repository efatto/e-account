# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _, fields, exceptions


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_number(self):
        res = super(AccountInvoice, self).action_number()
        for invoice in self:
            # ----- Only for supplier invoices and refunds
            if invoice.type in ('in_invoice', 'in_refund'):
                supplier_invoice_ids = self.search([
                    ('type', '=', invoice.type),
                    ('date_invoice', '=', invoice.date_invoice),
                    ('supplier_invoice_number', '=',
                     invoice.supplier_invoice_number),
                    ('partner_id', '=', invoice.partner_id.id),
                    ('company_id', '=', invoice.company_id.id),
                    ('id', '!=', invoice.id),
                ])
                if supplier_invoice_ids:
                    raise exceptions.Warning(
                        _('Cannot register invoice! This is a duplicate of '
                          '%s invoice registration.')
                        % ', '.join(supplier_invoice_ids.mapped('number')))
        return res
