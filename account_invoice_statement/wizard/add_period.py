# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, _, api, exceptions


class AddPeriod(models.TransientModel):
    _name = 'add.period.to.invoice.statement'

    period_id = fields.Many2one(
        'account.period', 'Period', required=True)

    @api.multi
    def add_period(self):
        data = self.read()[0]
        # if 'active_id' not in context:
        #     raise orm.except_orm(_('Error'),_('Current statement not found'))
        # statement_pool = self.pool.get('account.vat.period.end.statement')
        # wizard = self.browse(cr, uid, ids, context)[0]
        if self.period_id.invoice_statement_id:
            raise exceptions.ValidationError(
                _('Period %s is associated to statement %s yet') %
                (self.period_id.name,
                 self.period_id.invoice_statement_id.sender_date_commitment)
            )
        self.period_id.write({
            'invoice_statement_id': self._context['active_id']})
        return {
            'type': 'ir.actions.act_window_close',
        }
