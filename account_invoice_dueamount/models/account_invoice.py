# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    dueamount_line = fields.One2many(
        comodel_name='account.invoice.dueamount.line',
        inverse_name='invoice_id',
        string='Due amounts',
    )

    @api.multi
    def dueamount_set(self):
        for invoice in self:
            if invoice.payment_term and invoice.amount_total:
                totlines = invoice.payment_term.compute(
                    invoice.amount_total, invoice.date_invoice or False)[0]
                dueamount_line_obj = self.env['account.invoice.dueamount.line']
                dueamount_lines = dueamount_line_obj.search([
                    ('invoice_id', '=', invoice.id)])
                if dueamount_lines:
                    dueamount_lines.unlink()
                # create lines
                for due_line in totlines:
                    dueamount_line_obj.create({
                        'date': due_line[0], 'amount': due_line[1],
                        'invoice_id': invoice.id})

    #todo if the sum is = total invoice, must be used as
    #todo payments

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        # totlines = False
        # total_amount = 0
        # todo: compare dueamount_line with move_lines in date_maturity & amount
        # todo check total amount lines == invoice.amount_total
        dueamount_ids = self.dueamount_line.ids
        for line in move_lines:
            if line[2].get('date_maturity', False):
                amount = (line[2]['credit'] > 0 and line[2]['credit'] or
                          line[2]['debit'])
                # only for move lines with date_maturity (and partner?)
                for dueamount_line in self.dueamount_line:
                    if amount == dueamount_line.amount:
                        line[2].update({'date_maturity': dueamount_line.date})
                        dueamount_ids.remove(dueamount_line.id)
                        break
        return move_lines


class AccountInvoiceDueamountLine(models.Model):
    _name = 'account.invoice.dueamount.line'

    amount = fields.Float()
    date = fields.Date()
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice'
    )
