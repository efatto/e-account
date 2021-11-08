# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions, workflow


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

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
                    invoice_line.name = \
                        self.with_context({
                          'lang': inv.partner_id.lang}
                        )._translate_advance(percentage=True) % (
                          self.amount) + description
                    if self.sal_id:
                        invoice_line.account_analytic_sal_id = self.sal_id
            if self._context.get('open_invoices', False):
                return self.open_invoices(inv_ids)
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()


class SaleOrderLineMakeInvoice(models.TransientModel):
    _inherit = "sale.order.line.make.invoice"

    def make_invoices(self, cr, uid, ids, context=None):
        if context is None: context = {}
        res = False
        invoices = {}

        def make_invoice(order, lines):
            inv = self._prepare_invoice(cr, uid, order, lines)
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv)
            return inv_id

        sales_order_line_obj = self.pool.get('sale.order.line')
        sales_order_obj = self.pool.get('sale.order')
        for line in sales_order_line_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                if not line.order_id in invoices:
                    invoices[line.order_id] = []
                line_id = sales_order_line_obj.invoice_line_create(cr, uid, [line.id])
                for lid in line_id:
                    invoices[line.order_id].append(lid)
        for order, il in invoices.items():
            res = make_invoice(order, il)
            cr.execute('INSERT INTO sale_order_invoice_rel \
                    (order_id,invoice_id) values (%s,%s)', (order.id, res))
            sales_order_obj.invalidate_cache(cr, uid, ['invoice_ids'], [order.id], context=context)
            flag = True
            sales_order_obj.message_post(cr, uid, [order.id], body=_("Invoice created"), context=context)
            data_sale = sales_order_obj.browse(cr, uid, order.id, context=context)
            for line in data_sale.order_line:
                if not line.invoiced and line.state != 'cancel':
                    flag = False
                    break
            if flag:
                line.order_id.write({'state': 'progress'})
                workflow.trg_validate(uid, 'sale.order', order.id, 'all_lines', cr)

        if not invoices:
            raise exceptions.ValidationError(
                _('Invoice cannot be created for this Sales Order Line due to'
                  ' one of the following reasons:\n1.The state of this sales '
                  'order line is either "draft" or "cancel"!\n2.The Sales '
                  'Order Line is Invoiced!'))
        # Add sal_id to invoice lines
        for inv in self.pool['account.invoice'].browse(cr, uid, res, context=context):
            for line in inv.invoice_line:
                wiz = self.browse(cr, uid, ids, context=context)
                line.account_analytic_sal_id = wiz[0].sal_id
        # End modification
        if context.get('open_invoices', False):
            return self.open_invoices(cr, uid, ids, res, context=context)
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def _get_project(self):
        order_line_ids = self.env['sale.order.line'].browse(
            self._context['active_ids'])
        order_ids = order_line_ids.mapped('order_id')
        project_ids = order_ids.mapped('project_id')
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
