# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_order(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        return sale_orders

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
    sal_id = fields.Many2one(
        comodel_name='account.analytic.sal',
        string='SAL',
        help='Select sal line to link to invoice line'
    )

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount)
        if self.sal_id:
            for invoice_line in invoice.invoice_line_ids:
                invoice_line.account_analytic_sal_id = self.sal_id
        return invoice
