# -*- coding: utf-8 -*-
from openerp import api, fields, models
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # (08:57:50) laura@giobagnara.com: accessibile solo dall'utente egli solo può
    # scrivere , ma tutti leggono, in condivisione
    # (09:00:19) Sergio@efatto.it: cioè la colonna 'MARTA' deve poter scriverci
    # solo Marta?
    # (09:00:24) laura@giobagnara.com: esatto

    giorgio_note = fields.Char()
    fabrizio_note = fields.Char()
    chiara_note = fields.Char()
    marta_note = fields.Char()
    ammne_note = fields.Char()
    produz_note = fields.Char()
    magaz_note = fields.Char()
    payment_date = fields.Date(
        compute='_compute_payment_date',
        store=True)
    requested_date_limit = fields.Date(
        compute='_compute_requested_date_limit',
        store=True)

    @api.multi
    @api.depends('advance_invoice_ids')
    def _compute_payment_date(self):
        for order in self:
            payment_date = False
            if order.payment_term.id == self.env.ref(
                    'l10n_it_simplerp.payment_direct_30_days').id:
                payment_date = order.date_confirm
            else:
                paid_invoices = order.advance_invoice_ids.filtered(
                    lambda x: x.state == 'paid' and x.payment_ids)
                if paid_invoices:
                    payment_date = paid_invoices[0].payment_ids[0].date
            order.payment_date = payment_date

    @api.multi
    @api.depends('payment_date')
    def _compute_requested_date_limit(self):
        for order in self:
            if order.payment_date:
                order.requested_date_limit = fields.Datetime.to_string(
                    fields.Date.from_string(order.payment_date) + relativedelta(days=42)
                )
            else:
                order.requeste_date_limit = False

    @api.multi
    def open_sale_order_lines(self):
        self.ensure_one()
        action_name = 'sale_order_line_menu_usability.action_order_line_tree2'
        action = self.env.ref(action_name)
        action = action.read()[0]
        action['domain'] = [('id', 'in', self.order_line.ids)]
        return action
