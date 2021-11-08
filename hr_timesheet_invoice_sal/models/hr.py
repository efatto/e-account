# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class HrTimesheetInvoiceCreate(models.TransientModel):
    _inherit = "hr.timesheet.invoice.create"

    @api.model
    def _get_project(self):
        analytic_line_ids = self.env['account.analytic.line'].browse(
            self._context['active_ids'])
        project_ids = analytic_line_ids.mapped('account_id')
        if len(project_ids) != 1:
            return False
        return project_ids

    project_id = fields.Many2one(
        comodel_name='account.analytic.account',
        default=_get_project
    )
    sal_id = fields.Many2one(
        comodel_name='account.analytic.sal',
        string='SAL',
        help='Select sal line to link to invoice line'
    )

    @api.multi
    def do_create(self):
        res = super(HrTimesheetInvoiceCreate, self).do_create()
        if self.sal_id:
            invoices = self.env['account.invoice'].search(res['domain'])
            for invoice in invoices:
                invoice.invoice_line.account_analytic_sal_id = self.sal_id
        return res
