# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        """ Remove from computed amount not printable values on taxes
        """
        super(AccountInvoice, self)._compute_amount()
        self.amount_untaxed = 0.0
        for line in self.invoice_line:
            for tax_line in line.invoice_line_tax_id:
                if not (tax_line.tax_code_id.exclude_from_registries
                        or tax_line.tax_code_id.notprintable or
                        tax_line.tax_code_id.withholding_type or
                        tax_line.base_code_id.exclude_from_registries or
                        tax_line.base_code_id.notprintable or
                        tax_line.base_code_id.withholding_type):
                    self.amount_untaxed += line.price_subtotal
                    # if at least 1 tax is valid we take the amount
                    break
        self.amount_tax = sum(line.amount for line in self.tax_line.filtered(
            lambda x: not (
                x.tax_code_id.exclude_from_registries or
                x.tax_code_id.notprintable or
                x.tax_code_id.withholding_type or
                x.base_code_id.exclude_from_registries or
                x.base_code_id.notprintable or
                x.base_code_id.withholding_type
            )))
        self.amount_total = self.amount_untaxed + self.amount_tax

    amount_untaxed = fields.Float(compute=_compute_amount)
    amount_tax = fields.Float(compute=_compute_amount)
    amount_total = fields.Float(compute=_compute_amount)

