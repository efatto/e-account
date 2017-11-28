# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def name_get(self):
        result = super(AccountInvoice, self).name_get()
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Supplier Invoice'),
            'out_refund': _('Refund'),
            'in_refund': _('Supplier Refund'),
        }
        for inv in self:
            result.append((inv.id, "%s %s" % (
                inv.number or TYPES[inv.type],
                inv.name and (inv.name[:90] + '...') or '')))
        return result
