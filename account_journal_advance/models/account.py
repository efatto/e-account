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
    downpayment = fields.Selection([
        ('down_payment_intra', 'Down payment Intra CEE'),
        ('down_payment_extra', 'Down payment Extra CEE'),
        ('down_payment_it', 'Down payment Italy'),
    ], string='Down Payment type')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        """ create invoices for the active sales orders """
        if not self.product_id.downpayment:
            return super(SaleAdvancePaymentInv, self).create_invoices()
        else:
            if self.advance_payment_method in ('fixed', 'percentage'):
                inv_ids = []
                for sale_id, inv_values in self._prepare_advance_invoice_vals():
                    inv_ids.append(self._create_invoices(inv_values, sale_id))
                # add logic to change journal if it is downpayment
                fiscal_document_type_id = self.env[
                    'fiscal.document.type'].search([
                        ('code', '=', 'TD02')
                    ])
                for inv in self.env['account.invoice'].browse(inv_ids):
                    if self.product_id.downpayment:
                        journal_id = self.env['account.journal'].search([
                            ('downpayment', '=', self.product_id.downpayment)
                        ], limit=1)
                        if journal_id:
                            inv.write({'journal_id': journal_id.id})
                            inv.button_reset_taxes()
                        if fiscal_document_type_id:
                            inv.write({'fiscal_document_type_id':
                                       fiscal_document_type_id.id})
                # end
                if self._context.get('open_invoices', False):
                    return self.open_invoices(inv_ids)
                return {'type': 'ir.actions.act_window_close'}
