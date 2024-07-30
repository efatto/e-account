
from odoo import _, api, fields, models
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super().action_confirm()
        self.mapped("order_progress_ids")._refresh_cashflow_line()
        return res

    @api.multi
    def action_cancel(self):
        res = super().action_cancel()
        self.mapped('order_progress_ids')._refresh_cashflow_line()
        return res

    @api.multi
    def action_draft(self):
        res = super().action_draft()
        self.mapped('order_progress_ids')._refresh_cashflow_line()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for sale_order in self:
            if (
                vals.get('date_progress_end')
            ):
                sale_order.order_line._refresh_cashflow_line()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _refresh_cashflow_line(self):
        lines_to_do = self.filtered(lambda x: not x.order_id.order_progress_ids)
        super(SaleOrderLine, lines_to_do)._refresh_cashflow_line()


class SaleOrderProgress(models.Model):
    _inherit = "sale.order.progress"

    cashflow_line_ids = fields.One2many(
        comodel_name="mis.cash_flow.forecast_line",
        inverse_name="sale_order_progress_id",
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
            vals.get("offset_month")
            or vals.get("is_advance")
            or vals.get("amount_percent")
            or vals.get("amount_toinvoice_manual")
            or vals.get("invoiced")
            or vals.get("payment_term_id")
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
                if line.residual_toinvoice < 0:
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

            # check if line is to be excluded
            if line.invoiced or not line.residual_toinvoice:
                continue
            # with this value compute not invoiced amount (delivered or not)
            # residual balance must be computed on cashflow line as it depends on
            # current invoice factor and currency rate
            # residual_balance = actual_row_balance *
            # (1 - (line.qty_invoiced / max_qty))

            if not float_is_zero(
                line.residual_toinvoice,
                precision_rounding=line.order_id.currency_id.rounding,
            ):
                totlines = [
                    (
                        line.date.strftime("%Y-%m-%d"),
                        line.residual_toinvoice,
                    )
                ]
                if line.payment_term_id:
                    totlines = line.payment_term_id.compute(
                        line.residual_toinvoice,
                        line.date,
                    )[0]
                max_date_due = fields.Date.from_string(max([x[0] for x in totlines]))
                if max_date_due < first_day_current_month:
                    # do not create cashflow lines for dates before current month
                    continue
                for i, dueline in enumerate(totlines, start=1):
                    line.write({
                        "cashflow_line_ids": [
                            (0, 0, {
                                "name": _("Due line sale order progress #%s/%s %s") % (
                                    i, len(totlines), line.order_id.name),
                                "date": dueline[0],
                                "sale_balance_currency": dueline[1],
                                "currency_id": line.order_id.currency_id.id,
                                "balance": 0,
                                "sale_order_progress_id": line.id,
                                "account_id": account_id.id,
                                "partner_id": line.order_id.partner_id.id,
                                "res_id": line.id,
                                "res_model_id": self.env.ref(
                                    "sale_order_progress.model_sale_order_progress"
                                ).id,
                            })
                        ]
                    })
