# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    advance_description = fields.Char(
        string='Description for advance documents',
        size=64, translate=True,)
    downpayment = fields.Boolean()


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        """ create invoices for the active sales orders """
        res = super(SaleAdvancePaymentInv, self).create_invoices()
        if not self.product_id.downpayment:
            return res
        else:
            if self.advance_payment_method in ('fixed', 'percentage'):
                inv_ids = []
                for sale_id, inv_values in self._prepare_advance_invoice_vals():
                    inv_ids.append(self._create_invoices(inv_values, sale_id))
                # add logic to change journal if it is downpayment
                for inv in self.env['account.invoice'].browse(inv_ids):
                    if self.product_id.downpayment:
                        journal_id = self.env['account.journal'].search([
                            ('downpayment', '=', True)
                        ], limit=1)
                        if journal_id:
                            inv.write({'journal_id': journal_id.id})
                            inv.button_reset_taxes()
                # end
                if self._context.get('open_invoices', False):
                    return self.open_invoices(inv_ids)
                return {'type': 'ir.actions.act_window_close'}
