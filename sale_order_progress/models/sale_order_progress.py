from odoo import api, fields, models
from odoo.tools.date_utils import relativedelta
from odoo.tools import float_compare


class SaleOrderProgress(models.Model):
    _name = "sale.order.progress"
    _description = "Sale Order Progress"
    _order = "offset_month"

    name = fields.Char(string="Name", required=True)
    is_advance = fields.Boolean(string="Is an advance?")
    amount_percent = fields.Float(string="Amount (%)")
    order_id = fields.Many2one(
        comodel_name="sale.order",
        ondelete="cascade",
        required=True,
        string="Order",
    )
    # il related su order_id.currency_id crea un errore sull'eliminazione del primo
    # record dall'ordine di vendita, non ho trovato il motivo
    currency_id = fields.Many2one(
        compute="_compute_currency_id",
        comodel_name="res.currency",
        depends=["order_id.currency_id"],
        string="Currency",
        readonly=True,
        store=True,
    )
    amount_toinvoice_manual = fields.Monetary(string="Amount (manual)")
    amount_advance_toreturn = fields.Monetary(
        string="Amount advance to return",
        compute="_compute_invoiced",
        store=True,
    )
    amount_toinvoice = fields.Monetary(
        'Amount to invoice',
        compute="_compute_invoiced",
        store=True)
    amount_invoiced = fields.Monetary(
        string="Amount invoiced",
        compute="_compute_invoiced",
        store=True)
    residual_toinvoice = fields.Monetary(
        'Residual to invoice after advance return',
        compute="_compute_invoiced",
        store=True)
    invoiced = fields.Boolean(
        string='Invoiced',
        compute="_compute_invoiced",
        store=True,
        help='Sale order progress is marked invoiced when amount invoice lines linked '
             'to sale order progress is almost equal to the sale order progress amount.'
             '\nIt can be marked manually only if not already invoiced.'
    )
    invoiced_manual = fields.Boolean(
        string="Force invoiced",
    )
    offset_month = fields.Integer(
        string="Offset months (+/-)",
        help="Number of months with positive (forward) or negative (backward) value "
             "used to compute the foreseen invoicing date of this line starting from "
             "the commitment date month."
    )
    date = fields.Date(
        compute="_compute_date",
        string="Date",
        store=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Payment term",
    )

    @api.onchange("amount_toinvoice_manual")
    def _onchange_amount_toinvoice_manual(self):
        if self.amount_toinvoice_manual:
            self.amount_percent = 0

    @api.onchange("amount_percent")
    def _onchange_amount_percent(self):
        if self.amount_percent:
            self.amount_toinvoice_manual = 0

    @api.multi
    @api.depends(
        'offset_month',
        'order_id.date_progress_end',
        'order_id.date_order',
    )
    def _compute_date(self):
        for progress in self:
            progress.date = ((
                progress.order_id.date_progress_end
                or progress.order_id.date_order.date()
            ) + relativedelta(
                months=progress.offset_month))

    @api.multi
    @api.depends(
        'amount_toinvoice_manual',
        'amount_percent',
        'date',
        'invoiced_manual',
        'is_advance',
        'order_id.amount_total',
        'order_id.total_advance_percent',
        'order_id.order_line.price_total',
        'order_id.order_line.invoice_lines.price_total',
        'order_id.order_line.invoice_lines.invoice_id.state',
    )
    def _compute_invoiced(self):
        for progress in self.sorted(key="date"):
            progress.amount_invoiced = 0
            progress.residual_toinvoice = 0
            progress.amount_advance_toreturn = 0
            progress.invoiced = False
            order_id = progress.order_id
            if order_id:
                for line in order_id.mapped("order_line.invoice_lines").filtered(
                    lambda x: x.sale_order_progress_id == progress
                ):
                    progress.amount_invoiced += line.price_total
                # set amount_toinvoice if amount_percent is set
                if progress.amount_toinvoice_manual:
                    progress.amount_toinvoice = progress.amount_toinvoice_manual
                elif progress.amount_percent:
                    progress.amount_toinvoice = (
                        order_id.amount_total * progress.amount_percent / 100)
                progress.residual_toinvoice = (
                    progress.amount_toinvoice - progress.amount_invoiced
                    - (
                        progress.amount_advance_toreturn
                        if not progress.is_advance
                        else 0
                    )
                )
                if progress.invoiced_manual or (
                    progress.amount_invoiced >= progress.amount_toinvoice > 0.0
                ):
                    progress.invoiced = True
                amount_advance_toreturn = (
                    progress.amount_toinvoice
                    * order_id.total_advance_percent
                    / 100.0
                ) if not progress.is_advance else 0
                current_advance_toreturn_total = sum(
                    order_id.order_progress_ids.filtered(
                        lambda x: x != progress
                    ).mapped("amount_advance_toreturn")
                )  # put in the last order progress the difference of advance amount
                if (float_compare(
                    current_advance_toreturn_total + amount_advance_toreturn,
                    order_id.total_advance_amount,
                    precision_rounding=progress.currency_id.rounding,
                ) != 0
                    and progress == order_id.order_progress_ids.sorted(key="date")[-1]
                ):
                    progress.amount_advance_toreturn = (
                        order_id.total_advance_amount
                        - current_advance_toreturn_total
                    )
                else:
                    progress.amount_advance_toreturn = amount_advance_toreturn

    @api.multi
    def _compute_currency_id(self):
        for progress in self:
            progress.currency_id = progress.order_id.currency_id
