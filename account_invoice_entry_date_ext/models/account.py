# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, _, fields, api, exceptions


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        for inv in self:
            date_invoice = inv.date_invoice
            reg_date = inv.registration_date
            period_id = False
            if not inv.registration_date:
                if not inv.date_invoice:
                    reg_date = fields.Date.context_today(inv)
                else:
                    reg_date = inv.date_invoice

            if date_invoice and reg_date:
                if date_invoice > reg_date:
                    raise exceptions.Warning(_(
                        "The invoice date cannot be later than the"
                        " date of registration!"))

            date_start = inv.registration_date or inv.date_invoice \
                or fields.Date.context_today(inv)
            date_stop = inv.registration_date or inv.date_invoice \
                or fields.Date.context_today(inv)

            period_ids = self.env['account.period'].search(
                [
                    ('date_start', '<=', date_start),
                    ('date_stop', '>=', date_stop),
                    ('company_id', '=', inv.company_id.id)
                    ])
            if period_ids:
                period_id = period_ids[0]
            else:
                raise exceptions.Warning(_(
                    "Period do not exists for the registration date"
                    " entered! Change date of registration or create"
                    " the period."))
            self.write(
                {'registration_date': reg_date, 'period_id': period_id.id})

        super(AccountInvoice, self).action_move_create()

        for inv in self:
            for line in inv.move_id.line_id:
                line.write({
                    'ref': inv.supplier_invoice_number and
                    inv.supplier_invoice_number or ''})

        return True

    @api.onchange('date_invoice')
    def onchange_invoice_date(self):
        current_fy = self.env['account.fiscalyear'].find(
            dt=fields.Date.context_today(self))
        registration_fy = self.env['account.fiscalyear'].find(
            dt=self.date_invoice)

        if current_fy != registration_fy and not self.registration_date:
            return {
                'value': {},
                'warning': {
                    'title': 'Period selected is not in current fy !',
                    'message': '''If the registration date is null,
                    it will be filled with invoice date and period of
                    registration will be on a different fiscal year.
                    If it is not intended to do so, please fix registration
                    date.'''
                }
            }

    @api.model
    def _prepare_refund(
        self, invoice, date=None, period_id=None, description=None,
            journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date=date, period_id=period_id, description=description,
            journal_id=journal_id
        )
        #TODO pass if it is a customer refund
        if 'supplier_invoice_number' not in res:
            res['supplier_invoice_number'] = \
                _('Refund_') + self.supplier_invoice_number if \
                self.supplier_invoice_number else ''
        return res
