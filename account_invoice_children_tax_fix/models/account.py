# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _
from decimal import Decimal, ROUND_HALF_UP


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    def compute_all(self, price_unit, quantity, product=None,
                    partner=None, force_excluded=False):
        res = super(AccountTax, self).compute_all(
            price_unit, quantity, product=product, partner=partner,
            force_excluded=force_excluded)
        # Re-compute amounts for children taxes, so check only if taxes are 2
        tax_list = res['taxes']
        if len(tax_list) == 2:
            precision = 2  # It must always be 2 for euro companies
            total_original = res['total']
            total_included_original = res['total_included']
            rounded_tax_amount = 0.0
            for tax in tax_list:
                rounded_tax_amount += float(Decimal(
                    str(tax['amount'])).quantize(Decimal(
                        '1.' + precision * '0'), rounding=ROUND_HALF_UP))
            tax_difference_decimal = float(Decimal(
                str(total_included_original)).quantize(Decimal(
                    '1.' + precision * '0'), rounding=ROUND_HALF_UP)) \
                - total_original - rounded_tax_amount
            tax_difference = float(Decimal(
                str(tax_difference_decimal)).quantize(Decimal(
                    '1.' + precision * '0'), rounding=ROUND_HALF_UP))
            for tax in [x for x in tax_list if x['account_collected_id']]:
                if abs(tax_difference) != 0.0:
                    tax['amount'] = tax['amount'] + tax_difference
                tax_difference = 0.0
        return res