# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config, float_is_zero, float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super().action_confirm()
        self.mapped("order_line")._refresh_cashflow_line()
        return res

    @api.multi
    def action_cancel(self):
        res = super().action_cancel()
        self.mapped('order_line')._refresh_cashflow_line()
        return res

    @api.multi
    def action_draft(self):
        res = super().action_draft()
        self.mapped('order_line')._refresh_cashflow_line()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for sale_order in self:
            if (
                vals.get("payment_term_id")
                or vals.get("commitment_date")
                or vals.get("payment_mode_id")
            ):
                sale_order.order_line._refresh_cashflow_line()
        return res

    @api.constrains("payment_mode_id")
    def _check_payment_mode(self):
        if not config["test_enable"] or self.env.context.get(
            "test_mis_builder_cash_flow_sale"
        ):
            for record in self:
                if (
                    record.payment_mode_id
                    and record.payment_mode_id.bank_account_link != "fixed"
                ):
                    raise ValidationError(
                        _("Payment mode %s used in sale orders must be of type fixed.")
                        % record.payment_mode_id.name
                    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cashflow_line_ids = fields.One2many(
        comodel_name="mis.cash_flow.forecast_line",
        inverse_name="sale_line_id",
        string="Forecast cashflow line",
    )

    @api.model
    def create(self, vals):
        line = super().create(vals)
        line._refresh_cashflow_line()
        return line

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if (
            vals.get("price_unit")
            or vals.get("commitment_date")
            or vals.get("product_uom_qty")
            or vals.get("discount")
            or vals.get("discount2")
            or vals.get("discount3")
        ):
            self._refresh_cashflow_line()
        return res

    @api.multi
    def _refresh_cashflow_line(self):
        first_day_current_month = fields.Date.today().replace(day=1)
        for line in self:
            line.cashflow_line_ids.unlink()
            if line.order_id.state == "cancel":
                # do not create cashflow lines for cancelled SO
                continue
            if line.order_id.payment_mode_id.fixed_journal_id:
                journal_id = line.order_id.payment_mode_id.fixed_journal_id
                if line.price_total < 0:
                    account_id = journal_id.default_credit_account_id
                else:
                    account_id = journal_id.default_debit_account_id
            else:
                account_ids = self.env["account.account"].search(
                    [
                        (
                            "user_type_id",
                            "=",
                            self.env.ref("account.data_account_type_liquidity").id,
                        ),
                        ("company_id", "=", line.order_id.company_id.id),
                    ],
                    limit=1,
                )
                if not account_ids:
                    return False
                account_id = account_ids[0]

            # check is there is a residual prevision of amount to pay
            # compute actual value of sale_order row
            # as price_total do not change if delivered is more than ordered
            # (net unit price row * max between ordered and invoiced qty)
            max_qty = max([line.product_uom_qty, line.qty_delivered, 1])
            sale_balance_total_currency = (
                float_round(
                    line.price_total / (line.product_uom_qty or 1),
                    precision_rounding=line.order_id.currency_id.rounding,
                )
            ) * max_qty
            # with this value compute not invoiced amount (delivered or not)
            # residual balance must be computed on cashflow line as it depends on
            # current invoice factor and currency rate
            # residual_balance = actual_row_balance *
            # (1 - (line.qty_invoiced / max_qty))

            if not float_is_zero(
                sale_balance_total_currency,
                precision_rounding=line.order_id.currency_id.rounding,
            ):
                totlines = [
                    (
                        (
                            line.commitment_date
                            or line.order_id.commitment_date
                            or line.order_id.date_order
                        ).strftime("%Y-%m-%d"),
                        sale_balance_total_currency,
                    )
                ]
                if line.order_id.payment_term_id:
                    totlines = line.order_id.payment_term_id.compute(
                        sale_balance_total_currency,
                        line.commitment_date
                        or line.order_id.commitment_date
                        or line.order_id.date_order)[0]
                max_date_due = fields.Date.from_string(max([x[0] for x in totlines]))
                if max_date_due < first_day_current_month:
                    # do not create cashflow lines for dates before current month
                    continue
                for i, dueline in enumerate(totlines, start=1):
                    line.write({
                        "cashflow_line_ids": [
                            (0, 0, {
                                "name": _("Due line #%s/%s of Sale order %s") % (
                                    i, len(totlines), line.order_id.name),
                                "date": dueline[0],
                                "sale_balance_currency": dueline[1],
                                "currency_id": line.order_id.currency_id.id,
                                "balance": 0,
                                "sale_line_id": line.id,
                                "account_id": account_id.id,
                                "partner_id": line.order_id.partner_id.id,
                                "res_id": line.id,
                                "res_model_id": self.env.ref(
                                    "sale.model_sale_order_line"
                                ).id,
                            })
                        ]
                    })
