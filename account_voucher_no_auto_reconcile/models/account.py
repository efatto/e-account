# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def manual_reconcilation(self, **kwargs):
        for record in self.line_cr_ids:
            record['reconcile'] = False
            record['amount'] = 0.0
        for record in self.line_dr_ids:
            record['reconcile'] = False
            record['amount'] = 0.0


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    _order = 'date_original'
