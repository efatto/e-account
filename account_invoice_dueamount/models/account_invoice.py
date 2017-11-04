# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _
import copy


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

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        total_dueamount = 0
        # check total amount lines == invoice.amount_total
        for dueamount_line in self.dueamount_line:
            total_dueamount += dueamount_line.amount
        if total_dueamount != self.amount_total:
            raise exceptions.ValidationError(
                _('Total amount of due amount lines must be equal to '
                  'invoice total amount %d') % self.amount_total)

        # todo compare dueamount_line with move_lines in date_maturity & amount
        dueamount_ids = self.dueamount_line.ids
        maturity_move_lines = [
            l for l in move_lines if l[2].get('date_maturity', False)]
        maturity_lines_delta = len(maturity_move_lines) - len(dueamount_ids)

        if maturity_lines_delta > 0:
            # remove extra maturity lines from move_lines
            for line in move_lines:
                if line[2].get('date_maturity', False):
                    if maturity_lines_delta > 0:
                        move_lines.remove(line)
                        maturity_lines_delta -= 1
        # add extra move lines
        elif maturity_lines_delta < 0:
            for i in range(0, abs(maturity_lines_delta)):
                move_line_copy = copy.deepcopy(
                    tuple([maturity_move_lines[0]])
                )
                move_lines += move_line_copy

        dueamount_lines = self.env[
            'account.invoice.dueamount.line'].browse(dueamount_ids)
        i = 0
        for line in move_lines:
            if line[2].get('date_maturity', False):
                dueamount_line = dueamount_lines[i]
                is_credit = True if line[2]['credit'] > 0 else False
                line[2].update({'date_maturity': dueamount_line.date})
                if is_credit:
                    line[2].update({'credit': dueamount_line.amount})
                else:
                    line[2].update({'debit': dueamount_line.amount})
                i += 1

        return move_lines


class AccountInvoiceDueamountLine(models.Model):
    _name = 'account.invoice.dueamount.line'

    amount = fields.Float()
    date = fields.Date()
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice'
    )
