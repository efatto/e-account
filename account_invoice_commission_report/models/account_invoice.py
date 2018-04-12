# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _, fields, exceptions


class AccountInvoice(models.Model):
    """Invoice inherit to add salesman"""
    _inherit = "account.invoice"

    @api.depends('invoice_line.agents.amount')
    def _compute_commission_base_total(self):
        for record in self:
            record.commission_base_total = 0.0
            for line in record.invoice_line:
                record.commission_base_total += sum(
                    x.price_subtotal for x in line if line.agents)

    commission_base_total = fields.Float(
        string="Base Commissions", compute="_compute_commission_base_total",
        store=False)
