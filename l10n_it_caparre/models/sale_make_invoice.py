# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        """ create invoices for the active sales orders """
        if self.advance_payment_method in ('fixed', 'percentage'):
            inv_ids = []
            for sale_id, inv_values in self._prepare_advance_invoice_vals():
                inv_ids.append(self._create_invoices(inv_values, sale_id))
            # add logic to change journal if it is caparra
            for inv in self.env['account.invoice'].browse(inv_ids):
                if self.product_id.caparra:
                    journal_caparre_id = self.env['account.journal'].search([
                        ('caparre', '=', True)
                    ])
                    if journal_caparre_id:
                        inv.journal_id = journal_caparre_id
            # end
            if self._context.get('open_invoices', False):
                return self.open_invoices(inv_ids)
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()