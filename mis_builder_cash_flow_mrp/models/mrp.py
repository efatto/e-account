from odoo import _, api, fields, models
from odoo.tools import float_is_zero, safe_eval


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.multi
    def action_assign(self):
        res = super().action_assign()
        self.mapped('move_raw_ids')._refresh_cashflow_line()
        return res

    @api.multi
    def action_cancel(self):
        res = super().action_cancel()
        self.mapped('move_raw_ids')._refresh_cashflow_line()
        return res

    @api.multi
    def button_start_procurement(self):
        res = super().button_start_procurement()
        self.mapped('move_raw_ids')._refresh_cashflow_line()
        return res

    @api.multi
    def button_unreserve(self):
        res = super().button_unreserve()
        self.mapped('move_raw_ids')._refresh_cashflow_line()
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for production in self:
            if (
                vals.get('state')
                or vals.get('date_planned_start')
            ):
                production.move_raw_ids._refresh_cashflow_line()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    cashflow_line_ids = fields.One2many(
        comodel_name='mis.cash_flow.forecast_line',
        inverse_name='mrp_line_id',
        string='Forecast cashflow line',
    )

    @api.model
    def create(self, vals_list):
        line = super().create(vals_list)
        if line.raw_material_production_id:
            line._refresh_cashflow_line()
        return line

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if (
            vals.get('price_unit')
            or vals.get('date')
            or vals.get('date_expected')  # serve? lo lascio
            or vals.get('product_qty')
            or vals.get('state')
        ):
            self.filtered(
                lambda x: x.raw_material_production_id
            )._refresh_cashflow_line()
        return res

    @api.multi
    def _refresh_cashflow_line(self):
        first_day_current_month = fields.Date.today().replace(day=1)
        for line in self:
            company_currency_id = line.company_id.currency_id
            line.cashflow_line_ids.unlink()
            get_param = self.env['ir.config_parameter'].sudo().get_param
            param = get_param(
                'mis_builder_cash_flow_mrp.valid_states',
                '["confirmed", "planned", "progress"]',
            )
            if param and safe_eval(param):
                if line.raw_material_production_id.state not in safe_eval(param):
                    # do not create cashflow lines for order not in configured states
                    continue
            supplier_id = line.product_id.last_supplier_id
            if not supplier_id:
                supplier_id = line.product_id.seller_ids[0].name
            if supplier_id.supplier_payment_mode_id.fixed_journal_id:
                journal_id = supplier_id.supplier_payment_mode_id.fixed_journal_id
                if line.bom_line_id.price_subtotal < 0:
                    account_id = journal_id.default_credit_account_id
                else:
                    account_id = journal_id.default_debit_account_id
            else:
                account_ids = self.env["account.account"].search([
                    ('user_type_id', '=',
                     self.env.ref('account.data_account_type_liquidity').id),
                    ('company_id', '=', line.raw_material_production_id.company_id.id),
                ], limit=1)
                if not account_ids:
                    return False
                account_id = account_ids[0]

            # FIXME (this was the comment on purchase module):
            #  check if there is a residual prevision of amount to pay
            #  compute actual value of purchase_order row
            #  as price_total do not change if delivered is more than ordered
            #  (net unit price row * max between ordered and invoiced qty)
            #  add default vat
            totals = line.product_id.supplier_taxes_id.compute_all(
                line.bom_line_id.price_unit,
                company_currency_id,
                line.product_uom_qty,
                line.product_id,
            )
            mrp_balance_total_company_currency = totals["total_included"]

            if not float_is_zero(
                mrp_balance_total_company_currency,
                precision_rounding=company_currency_id.rounding,
            ):
                commitment_date = (
                    line.raw_material_production_id.date_planned_start or
                    line.raw_material_production_id.commitment_date or
                    line.raw_material_production_id.sale_id.commitment_date or
                    line.raw_material_production_id.sale_id.date_order)
                totlines = [(
                    commitment_date.strftime("%Y-%m-%d"),
                    mrp_balance_total_company_currency
                )]
                supplier_payment_term_id = supplier_id.property_supplier_payment_term_id
                if supplier_payment_term_id:
                    totlines = supplier_payment_term_id.compute(
                        mrp_balance_total_company_currency,
                        commitment_date)[0]
                max_date_due = fields.Date.from_string(max([x[0] for x in totlines]))
                if max_date_due < first_day_current_month:
                    # do not create cashflow lines for dates before current month
                    continue
                for i, dueline in enumerate(totlines, start=1):
                    line.write({
                        "cashflow_line_ids": [
                            (0, 0, {
                                "name": _("Due line #%s/%s of Mrp production %s") % (
                                    i, len(totlines),
                                    line.raw_material_production_id.name),
                                "date": dueline[0],
                                "mrp_balance_currency": dueline[1],
                                "currency_id": company_currency_id.id,
                                "balance": 0,
                                "mrp_line_id": line.id,
                                "account_id": account_id.id,
                                "partner_id": supplier_id.id,
                                "res_id": line.id,
                                "res_model_id": self.env.ref(
                                    "stock.model_stock_move").id,
                            })
                        ]
                    })
