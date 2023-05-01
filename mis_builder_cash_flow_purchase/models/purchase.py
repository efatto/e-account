# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_round


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for purchase_order in self:
            if vals.get('payment_term_id') or vals.get('date_planned') or vals.get(
                'payment_mode_id'
            ):
                for line in purchase_order.order_line:
                    line._refresh_cashflow_line()
        return res

    @api.constrains('payment_mode_id')
    def _check_payment_mode(self):
        for record in self:
            if record.payment_mode_id and \
                    record.payment_mode_id.bank_account_link != 'fixed':
                raise ValidationError(
                    _('Payment mode %s used in purchase orders must be of type fixed.')
                    % record.payment_mode_id.name
                )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    cashflow_line_ids = fields.One2many(
        comodel_name='mis.cash_flow.forecast_line',
        inverse_name='purchase_line_id',
        string='Forecast cashflow line',
    )

    @api.model
    def create(self, vals):
        line = super().create(vals)
        line._refresh_cashflow_line()
        return line

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('price_unit') or vals.get('date_planned') \
                or vals.get('product_qty') or vals.get('discount') \
                or vals.get('discount2') or vals.get('discount3'):
            for line in self:
                line._refresh_cashflow_line()
        return res

    @api.multi
    def _refresh_cashflow_line(self):
        self.ensure_one()
        self.cashflow_line_ids.unlink()
        cashflow_line_obj = self.env['mis.cash_flow.forecast_line']
        cashflow_line_ids = []
        if self.order_id.payment_mode_id.fixed_journal_id:
            journal_id = self.order_id.payment_mode_id.fixed_journal_id
            if self.price_total < 0:
                account_id = journal_id.default_credit_account_id
            else:
                account_id = journal_id.default_debit_account_id
        else:
            account_ids = self.env["account.account"].search([
                ('user_type_id', '=',
                 self.env.ref('account.data_account_type_liquidity').id),
                ('company_id', '=', self.order_id.company_id.id),
            ], limit=1)
            if not account_ids:
                return False
            account_id = account_ids[0]

        # check is there is a residual prevision of amount to pay
        # compute actual value of purchase_order row
        # as price_total do not change if delivered is more than ordered
        # (net unit price row * max between ordered and invoiced qty)
        max_qty = max([self.product_qty, self.qty_received, 1])
        purchase_balance_total_currency = (
            float_round(
                self.price_total / (self.product_qty or 1),
                precision_rounding=self.order_id.currency_id.rounding)
        ) * max_qty
        # with this value compute not invoiced amount (delivered or not)
        # residual balance must be computed on cashflow line as it depends on current
        # invoice factor and currency rate
        # residual_balance = actual_row_balance * (1 - (self.qty_invoiced / max_qty))

        if not float_is_zero(purchase_balance_total_currency,
                             precision_rounding=self.order_id.currency_id.rounding):
            totlines = [(
                (
                    self.date_planned or
                    self.order_id.date_planned or
                    self.order_id.date_order
                ).strftime("%Y-%m-%d"),
                purchase_balance_total_currency
            )]
            if self.order_id.payment_term_id:
                totlines = self.order_id.payment_term_id.compute(
                    purchase_balance_total_currency,
                    self.date_planned or self.order_id.date_planned or
                    self.order_id.date_order)[0]
            for i, dueline in enumerate(totlines, start=1):
                due_line_id = cashflow_line_obj.create([{
                    'name': _('Due line #%s/%s of Purchase order %s') % (
                        i, len(totlines), self.order_id.name),
                    'date': dueline[0],
                    'purchase_balance_currency': dueline[1],
                    'currency_id': self.order_id.currency_id.id,
                    'balance': 0,
                    'purchase_line_id': self.id,
                    'account_id': account_id.id,
                    'partner_id': self.order_id.partner_id.id,
                    'res_id': self.id,
                    'res_model_id': self.env.ref("base.model_ir_model").id,
                }])
                cashflow_line_ids.append(due_line_id.id)
