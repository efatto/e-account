# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        """ create invoices for the active sales orders """
        if self.advance_payment_method in ('fixed', 'percentage'):
            inv_ids = []
            for sale_id, inv_values in self._prepare_advance_invoice_vals():
                inv_ids.append(self._create_invoices(inv_values, sale_id))
            self.env['account.invoice'].browse(inv_ids).write(
                {'is_advance_invoice': True})
            if self._context.get('open_invoices', False):
                return self.open_invoices(inv_ids)
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()
