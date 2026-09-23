# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_round


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super().button_confirm()
        self.filtered(lambda x: x.state == "purchase").mapped(
            "order_line"
        )._refresh_cashflow_line()
        return res

    def write(self, vals):
        res = super().write(vals)
        for purchase_order in self:
            if (
                vals.get("payment_term_id")
                or vals.get("date_planned")
                or vals.get("payment_mode_id")
            ):
                purchase_order.order_line._refresh_cashflow_line()
        return res

    @api.constrains("payment_mode_id")
    def _check_payment_mode(self):
        for record in self:
            if (
                record.payment_mode_id
                and record.payment_mode_id.bank_account_link != "fixed"
            ):
                raise ValidationError(
                    _("Payment mode %s used in purchase orders must be of type fixed.")
                    % record.payment_mode_id.name
                )


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["purchase.order.line", "mis.cash_flow.mixin"]

    cashflow_line_ids = fields.One2many(
        comodel_name="mis.cash_flow.forecast_line",
        inverse_name="purchase_line_id",
        string="Forecast cashflow line",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._refresh_cashflow_line()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if (
            vals.get("price_unit")
            or vals.get("date_planned")
            or vals.get("product_qty")
            or vals.get("discount")
            or vals.get("discount2")  # noqa
            or vals.get("discount3")  # noqa
        ):
            self._refresh_cashflow_line()
        return res

    def _refresh_cashflow_line(self):
        debit_account_id = self._get_account("account_journal_payment_debit_account_id")
        credit_account_id = self._get_account(
            "account_journal_payment_credit_account_id"
        )
        for line in self:
            line.cashflow_line_ids.unlink()
            if line.order_id.payment_mode_id.fixed_journal_id:
                account_id = (
                    line.order_id.payment_mode_id.fixed_journal_id.bank_account_id.id
                )
            elif line.price_total < 0:
                account_id = credit_account_id
            else:
                account_id = debit_account_id

            # check is there is a residual prevision of amount to pay
            # compute actual value of purchase_order row
            # as price_total do not change if delivered is more than ordered
            # (net unit price row * max between ordered and invoiced qty)
            max_qty = max([line.product_qty, line.qty_received, 1])
            purchase_balance_total_currency = (
                float_round(
                    line.price_total / (line.product_qty or 1),
                    precision_rounding=line.order_id.currency_id.rounding,
                )
            ) * max_qty
            # with this value compute not invoiced amount (delivered or not)
            # residual balance must be computed on cashflow line as it depends on
            # current invoice factor and currency rate
            # residual_balance = actual_row_balance *
            # (1 - (line.qty_invoiced / max_qty))

            if not float_is_zero(
                purchase_balance_total_currency,
                precision_rounding=line.order_id.currency_id.rounding,
            ):
                totlines = {
                    "line_ids": [
                        {
                            "date": (
                                line.date_planned
                                or line.order_id.date_planned
                                or line.order_id.date_order
                            ),
                            "company_amount": purchase_balance_total_currency,
                        }
                    ]
                }
                if line.order_id.payment_term_id:
                    totlines = line.order_id.payment_term_id._compute_terms(
                        date_ref=line.date_planned
                        or line.order_id.date_planned
                        or line.order_id.date_order
                        or fields.Date.context_today(line),
                        currency=line.currency_id,
                        tax_amount_currency=purchase_balance_total_currency,
                        tax_amount=purchase_balance_total_currency,
                        untaxed_amount_currency=0,
                        untaxed_amount=0,
                        company=line.company_id,
                        sign=1,
                    )
                line.write(
                    {
                        "cashflow_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": _(
                                        "Due line #%(num)s/%(to)s of Purchase order "
                                        "%(po)s",
                                        num=i,
                                        to=len(totlines),
                                        po=line.order_id.name,
                                    ),
                                    "date": dueline["date"],
                                    "purchase_balance_currency": dueline[
                                        "company_amount"
                                    ],
                                    "currency_id": line.order_id.currency_id.id,
                                    "balance": 0,
                                    "purchase_line_id": line.id,
                                    "account_id": account_id,
                                    "partner_id": line.order_id.partner_id.id,
                                    "res_id": line.id,
                                    "res_model_id": self.env.ref(
                                        "purchase.model_purchase_order_line"
                                    ).id,
                                },
                            )
                            for i, dueline in enumerate(totlines["line_ids"], start=1)
                        ]
                    }
                )
