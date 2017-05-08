# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_order_lines(self):
        line_ids = self.env['sale.order'].browse(
            self._context['active_id']).order_line
        return line_ids

    @api.model
    def _get_order(self):
        order_id = self.env['sale.order'].browse(
            self._context['active_id'])
        return order_id

    @api.onchange('sal_id')
    def _get_sal_percent(self):
        if self.sal_id:
            self.amount = self.sal_id.percent_toinvoice

    order_id = fields.Many2one(
        comodel_name='sale.order',
        default=_get_order
    )
    project_id = fields.Many2one(
        related='order_id.project_id'
    )
    order_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        relation='advance_sale_order_line_rel_sal',
        column1='order_line_id', column2='advance_id',
        string='Order lines',
        default=_get_order_lines,
        help='Select order lines to print details in invoice'
    )
    sal_id = fields.Many2one(
        comodel_name='account.analytic.sal',
        string='SAL',
        help='Select sal line to link to invoice line'
    )

    @api.multi
    def create_invoices(self):
        """ create invoices for the active sales orders """
        if self.advance_payment_method in ('fixed', 'percentage'):
            inv_ids = []
            for sale_id, inv_values in self._prepare_advance_invoice_vals():
                inv_ids.append(self._create_invoices(inv_values, sale_id))
            for inv in self.env['account.invoice'].browse(inv_ids):
                if self.order_line_ids:
                    description = ''
                    for line in self.order_line_ids:
                        description += ('\n' + line.name)
                for invoice_line in inv.invoice_line:
                    invoice_line.name += description
                    if self.sal_id:
                        invoice_line.account_analytic_sal_id = self.sal_id
            if self._context.get('open_invoices', False):
                return self.open_invoices(inv_ids)
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()
