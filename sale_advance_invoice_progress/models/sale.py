# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions, workflow
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import time
from datetime import datetime


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_payment_method(self):
        order_id = self.env['sale.order'].browse(
            self._context['active_id'])
        if order_id.order_policy == 'picking':
            return [('percentage','Percentage'),
                    ('fixed','Fixed price (deposit)'),]
        else:
            return [
                ('all', 'Invoice the whole sales order'),
                ('percentage','Percentage'), ('fixed','Fixed price (deposit)'),
                ('lines', 'Some order lines')]

    advance_payment_method = fields.Selection(
        selection=_get_payment_method,
        default=False,
    )


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
        order_invoiced_amount = {}
        for line in sales_order_line_obj.browse(cr, uid, context.get(
                'active_ids', []), context=context):
            if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                if not line.order_id in invoices:
                    invoices[line.order_id] = []
                line_id = sales_order_line_obj.invoice_line_create(
                    cr, uid, [line.id])
                for lid in line_id:
                    invoices[line.order_id].append(lid)
                    # get total amount invoiced for order
                    if not line.order_id.id in order_invoiced_amount:
                        order_invoiced_amount[line.order_id.id] = \
                            line.price_subtotal
                    else:
                        order_invoiced_amount[line.order_id.id] += \
                            line.price_subtotal
        order_invoice = {}
        for order, il in invoices.items():
            res = make_invoice(order, il)
            #
            if res not in order_invoice:
                order_invoice[res] = {
                    order.id: order_invoiced_amount[order.id]}
            if order.id not in order_invoice[res]:
                order_invoice[res].update(
                    {order.id: order_invoiced_amount[order.id]})
            # else:
            #     pass # ??? boh non credo possa esserci
            for advance_invoice in order.advance_invoice_ids:
                for preline in advance_invoice.invoice_line:
                    inv_line_id = self.pool['account.invoice.line'].copy(
                        cr, uid, preline.id, {
                            'invoice_id': res,
                            'price_unit': - order_invoice[res][order.id] *
                            order.advance_percentage / 100 *
                            preline.price_subtotal / order.advance_amount,
                            'advance_invoice_id': advance_invoice.id,
                        })
            #
            cr.execute('INSERT INTO sale_order_invoice_rel \
                    (order_id,invoice_id) values (%s,%s)', (order.id, res))
            sales_order_obj.invalidate_cache(
                cr, uid, ['invoice_ids'], [order.id], context=context)
            flag = True
            sales_order_obj.message_post(
                cr, uid, [order.id], body=_("Invoice created"),
                context=context)
            data_sale = sales_order_obj.browse(cr, uid, order.id,
                                               context=context)
            for line in data_sale.order_line:
                if not line.invoiced and line.state != 'cancel':
                    flag = False
                    break
            if flag:
                line.order_id.write({'state': 'progress'})
                workflow.trg_validate(
                    uid, 'sale.order', order.id, 'all_lines', cr)

        if not invoices:
            raise exceptions.ValidationError(
                _('Invoice cannot be created for this Sales Order Line due to'
                  ' one of the following reasons:\n1.The state of this sales '
                  'order line is either "draft" or "cancel"!\n2.The Sales '
                  'Order Line is Invoiced!'))

        if context.get('open_invoices', False):
            return self.open_invoices(cr, uid, ids, res, context=context)
        return {'type': 'ir.actions.act_window_close'}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_advance_invoices(self):
        order_line_obj = self.env['sale.order.line']
        for order in self:
            invoiced_sale_line_ids = order_line_obj.search(
                [('order_id', '=', order.id), ('invoiced', '=', True)],)

            order.from_line_invoice_ids = invoiced_sale_line_ids.mapped(
                'invoice_lines.invoice_id'
            )
            if order.from_line_invoice_ids:
                order.from_line_invoice_tag = \
                    str([str(x.number) + '(' + str(
                        sum(y.price_subtotal for y in x.invoice_line.filtered(
                            lambda z: not z.advance_invoice_id
                        ))) + ')' for x in order.from_line_invoice_ids])
                order.from_line_amount_residual = sum(
                    x.residual for x in order.from_line_invoice_ids
                )
            else:
                order.from_line_invoice_tag = _(u'(No invoiced lines yet)')

            order.advance_invoice_ids = order.invoice_ids.filtered(
                lambda x: x.state not in ('cancel',) and
                x not in order.from_line_invoice_ids
            )
            if order.advance_invoice_ids:
                order.advance_invoice_tag = \
                    str([str(x.number) + '(' + str(x.amount_untaxed) + ')' for
                         x in
                         order.advance_invoice_ids])
            else:
                order.advance_invoice_tag = _(u'(No advance invoice yet)')

            order.advance_amount = sum(
                x.amount_untaxed for x in order.advance_invoice_ids if x.type
                == 'out_invoice') - sum(
                x.amount_untaxed for x in order.advance_invoice_ids if x.type
                == 'out_refund')
            order.advance_amount_total = sum(
                x.amount_total for x in order.advance_invoice_ids if x.type
                == 'out_invoice') - sum(
                x.amount_total for x in order.advance_invoice_ids if x.type
                == 'out_refund')
            order.advance_residual = sum(
                x.residual for x in order.advance_invoice_ids if x.type
                == 'out_invoice') - sum(
                x.residual for x in order.advance_invoice_ids if x.type
                == 'out_refund')
            order.advance_percentage = \
                order.advance_amount / order.amount_untaxed * 100 if \
                order.advance_amount and order.amount_untaxed else 0.0
            order.refunded_invoice_line_ids = self.env[
                'account.invoice.line'].search([
                    ('advance_invoice_id', 'in', order.advance_invoice_ids.ids)
                    , ('invoice_id.state', 'in', ['open', 'paid'])
                ])
            order.advance_refunded_amount = sum(
                x.price_subtotal for x in order.refunded_invoice_line_ids if
                x.invoice_id.type == 'out_invoice'
            ) - sum(
                x.price_subtotal for x in order.refunded_invoice_line_ids if
                x.invoice_id.type == 'out_refund'
            )
            order.amount_residual = order.amount_total - \
                order.advance_amount_total + order.advance_residual

    advance_invoice_ids = fields.One2many(
        comodel_name='account.invoice',
        compute=_get_advance_invoices,
        translate=True
    )
    advance_invoice_tag = fields.Char(
        compute=_get_advance_invoices,
        string='Amount Advance by Invoice',
        translate=True,
    )
    from_line_invoice_ids = fields.One2many(
        comodel_name='account.invoice',
        compute=_get_advance_invoices,
        string='Invoices from Order',
        translate=True,
    )
    from_line_invoice_tag = fields.Char(
        compute=_get_advance_invoices,
        string='Amount Invoiced by Invoice',
        translate=True,
    )
    from_line_amount_residual = fields.Float(
        compute=_get_advance_invoices,
        string='Amount Invoiced not yet paid',
        translate=True,
    )
    refunded_invoice_line_ids = fields.One2many(
        comodel_name='account.invoice.line',
        compute=_get_advance_invoices,
        string='Invoice line advance refunded',
        translate=True,
    )
    advance_refunded_amount = fields.Float(
        compute=_get_advance_invoices, translate=True
    )
    advance_percentage = fields.Float(
        compute=_get_advance_invoices, translate=True
    )
    advance_amount = fields.Float(
        compute=_get_advance_invoices, translate=True
    )
    advance_amount_total = fields.Float(
        compute=_get_advance_invoices, translate=True
    )
    advance_residual = fields.Float(
        compute=_get_advance_invoices, translate=True
    )
    amount_residual = fields.Float(
        compute=_get_advance_invoices, translate=True
    )

    @api.cr_uid_context
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(
            cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)],
            context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(
                cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in \
                    from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(
                        cr, uid, preline.id, {
                            'invoice_id': False,
                            'price_unit': -preline.price_unit,
                            'advance_invoice_id': preinv.id,
                            'sequence': 0,
                            'name': (_('Ref. Advance Invoice n. %s dated %s') %
                                     (preinv.number,
                                      datetime.strptime(
                                          preinv.date_invoice,
                                          DEFAULT_SERVER_DATE_FORMAT).
                                          strftime("%d/%m/%Y")))
                        })
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        data = inv_obj.onchange_payment_term_date_invoice(
            cr, uid, [inv_id], inv['payment_term'],
            time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id
