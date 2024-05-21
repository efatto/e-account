from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('payment_mode_id')
    def _onchange_payment_mode_id(self):
        super()._onchange_payment_mode_id()
        pay_mode = self.payment_mode_id
        if (
            pay_mode and
            pay_mode.payment_type == 'outbound' and
            pay_mode.bank_account_link == 'fixed' and
            pay_mode.fixed_journal_id.bank_account_id
        ):
            self.partner_bank_id = pay_mode.fixed_journal_id.bank_account_id
