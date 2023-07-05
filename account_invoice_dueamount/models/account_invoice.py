# Copyright 2017-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, exceptions, fields, models
from odoo.tools import float_compare, float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    dueamount_line_ids = fields.One2many(
        comodel_name="account.invoice.dueamount.line",
        inverse_name="invoice_id",
        string="Due amounts",
    )

    def dueamount_set(self):
        for invoice in self:
            others_lines = invoice.line_ids.filtered(
                lambda inv_line: inv_line.account_id.account_type
                not in ("asset_receivable", "liability_payable")
            )
            company_currency_id = (
                invoice.company_id or invoice.env.company
            ).currency_id
            total_balance = sum(
                others_lines.mapped(lambda l: company_currency_id.round(l.balance))
            )
            if total_balance:
                if invoice.invoice_payment_term_id:
                    # context for compatibility w/
                    # account_payment_term_partner_holiday
                    totlines = invoice.invoice_payment_term_id.with_context(
                        currency_id=invoice.currency_id.id,
                        default_partner_id=invoice.partner_id.id,
                    ).compute(total_balance, invoice.invoice_date or False)
                else:
                    totlines = [(invoice.invoice_date, total_balance)]
                dueamount_line_obj = self.env["account.invoice.dueamount.line"]
                due_line_ids = []
                for line in totlines:
                    due_line_id = dueamount_line_obj.create(
                        {
                            "date": line[0],
                            "amount": -line[1],
                            "invoice_id": invoice.id,
                        }
                    )
                    due_line_ids.append(due_line_id.id)
                invoice.write({"dueamount_line_ids": [(6, 0, due_line_ids)]})

    def _post(self, soft=True):
        for move in self:
            if move.dueamount_line_ids:
                maturity_move_lines = move.line_ids.filtered(lambda x: x.date_maturity)
                if hasattr(move, "withholding_tax_amount"):
                    dueamount_line_obj = self.env["account.invoice.dueamount.line"]
                    missing_dueamount = move.amount_total - sum(
                        [x.amount for x in move.dueamount_line_ids]
                    )
                    if not float_is_zero(missing_dueamount, 2):
                        due_line_id = dueamount_line_obj.create(
                            [
                                {
                                    "date": move.invoice_date_due,
                                    "amount": missing_dueamount,
                                    "invoice_id": move.id,
                                }
                            ]
                        )
                        move.write({"dueamount_line_ids": [(4, due_line_id.id)]})
                # check total amount lines == invoice.amount_total
                total_dueamount = sum(move.dueamount_line_ids.mapped("amount"))
                if float_compare(total_dueamount, move.amount_total, 2) != 0:
                    raise exceptions.ValidationError(
                        _(
                            "Total amount of due amount lines must be equal to "
                            "invoice total amount %.2f"
                        )
                        % move.amount_total
                    )

                dueamount_ids = move.dueamount_line_ids.ids
                maturity_lines_delta = len(maturity_move_lines) - len(dueamount_ids)

                if maturity_lines_delta > 0:
                    # remove extra maturity lines from move_lines
                    for line in maturity_move_lines:
                        if maturity_lines_delta > 0:
                            maturity_move_lines -= line
                            line.with_context(check_move_validity=False).unlink()
                            maturity_lines_delta -= 1
                # add extra move lines
                elif maturity_lines_delta < 0:
                    for _i in range(0, abs(maturity_lines_delta)):
                        maturity_move_lines += (
                            maturity_move_lines[0]
                            .with_context(check_move_validity=False)
                            .copy()
                        )

                dueamount_lines = self.env["account.invoice.dueamount.line"].browse(
                    dueamount_ids
                )
                i = 0
                for line in maturity_move_lines:
                    dueamount_line = dueamount_lines[i]
                    credit_debit_field = "credit" if line.credit else "debit"
                    line.with_context(check_move_validity=False).update(
                        {
                            "date_maturity": dueamount_line.date,
                            credit_debit_field: dueamount_line.amount,
                        }
                    )
                    i += 1
        res = super()._post(soft=soft)
        return res


class AccountInvoiceDueamountLine(models.Model):
    _name = "account.invoice.dueamount.line"
    _description = "Account invoice due amount line"
    _rec_name = "date"
    _order = "date ASC"

    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice")
