# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class HrAnalyticTimesheet(models.Model):
    _inherit = "hr.analytic.timesheet"

    def _get_invoiceability(self):
        for ts in self:
            ts.invoiceable = False
            if ts.to_invoice and ts.to_invoice.factor < 100.0:
                ts.invoiceable = True

    invoice_state = fields.Selection(
        string="Invoice State", readonly=True,
        related='invoice_id.state'
    )
    invoiceable = fields.Boolean(
        compute='_get_invoiceability'
    )
