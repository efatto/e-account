# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    origin_invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Origin invoice line in case of refund')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.returns('self')
    def refund(self, date=None, period_id=None, description=None,
               journal_id=None):
        new_invoices = super(AccountInvoice, self).refund(
            date=date, period_id=period_id, description=description,
            journal_id=journal_id)
        for invoice in new_invoices:
            for line in invoice.invoice_line.filtered('origin_invoice_line_id'):
                # add refund invoice line to invoice_lines in sale order line
                # n.b. invoice_id in rel table is invoice_line_id !
                self._cr.execute(
                    'SELECT * from sale_order_line_invoice_rel '
                    'where invoice_id= %s'
                    % line.origin_invoice_line_id.id)
                sale_order_rels = self._cr.fetchall()
                for sale_order_rel in sale_order_rels:
                    for sale_order_line in self.env['sale.order.line'].browse(
                            sale_order_rel[0]):
                        sale_order_line.write(
                            {'invoice_lines': [(4, line.id)]})
                        sale_order_line.order_id.write(
                            {'invoice_ids': [(4, invoice.id)]})
        return new_invoices

    @api.model
    def _refund_cleanup_lines(self, lines):
        res = super(AccountInvoice, self)._refund_cleanup_lines(lines)
        if lines and lines[0]._name == 'account.invoice.line':
            for i, line in enumerate(lines):
                vals = res[i][2]
                vals['origin_invoice_line_id'] = line.id
        return res
