# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDueAmount(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
        self.today = fields.Date.today()
        self.sale_journal = (
            self.env["account.journal"]
            .with_company(self.env.user.company_id.id)
            .search(
                [
                    ("type", "=", "sale"),
                ],
                limit=1,
            )
        )
        self.purchase_journal = (
            self.env["account.journal"]
            .with_company(self.env.user.company_id.id)
            .search(
                [
                    ("type", "=", "purchase"),
                ],
                limit=1,
            )
        )
        self.revenue_account = self.env["account.account"].create(
            {
                "code": "TEST_REVENUE",
                "name": "Sale revenue",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.expense_account = self.env["account.account"].create(
            {
                "code": "TEST_EXPENSE",
                "name": "Purchase expense",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        self.payment_term_2rate = self.env["account.payment.term"].create(
            {
                "name": "Payment term 30/60 end of month",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "value": "percent",
                            "value_amount": 50,
                            "days": 30,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "value": "balance",
                            "days": 30,
                            "option": "after_invoice_month",
                        },
                    ),
                ],
            }
        )

    def create_invoice(self, move_type):
        invoice_line_data = {
            "product_id": self.env.ref("product.product_product_5").id,
            "quantity": 5,
            "account_id": move_type.startswith("out_")
            and self.revenue_account.id
            or self.expense_account.id,
            "name": "product test 5",
            "price_unit": 6,
            "currency_id": self.env.ref("base.EUR").id,
        }
        invoice = self.env["account.move"].create(
            {
                "move_type": move_type,
                "invoice_date": self.today,
                "currency_id": self.env.ref("base.EUR").id,
                "journal_id": move_type.startswith("out_")
                and self.sale_journal.id
                or self.purchase_journal.id,
                "company_id": self.env.user.company_id.id,
                "partner_id": self.partner.id,
                "invoice_line_ids": [(0, 0, invoice_line_data)],
                "invoice_payment_term_id": self.payment_term_2rate.id,
            }
        )
        return invoice

    def test_01_out_invoice(self):
        self._test_invoice("out_invoice")

    def test_02_out_refund(self):
        self._test_invoice("out_refund")

    def test_03_in_invoice(self):
        self._test_invoice("in_invoice")

    def test_04_in_refund(self):
        self._test_invoice("in_refund")

    def _test_invoice(self, move_type):
        # create invoice with payment term and check it is the default, then create
        # another invoice forcing due amounts
        invoice = self.create_invoice(move_type)
        invoice._post()
        self.assertEqual(len(invoice.line_ids.filtered(lambda x: x.date_maturity)), 2)
        invoice.button_draft()
        self.assertEqual(invoice.state, "draft")
        invoice.dueamount_set()
        self.assertEqual(len(invoice.dueamount_line_ids), 2)
        total_amount = sum(invoice.mapped("dueamount_line_ids.amount"))
        invoice.dueamount_line_ids[0].write(
            {
                "amount": 10.0,
            }
        )
        invoice.dueamount_line_ids[1].write(
            {
                "amount": total_amount - 10.0,
            }
        )
        invoice._post()
        inv_line_ids = invoice.line_ids.filtered(
            lambda x: x.account_id.user_type_id.type in ("receivable", "payable")
        )
        self.assertAlmostEqual(
            sum(invoice.mapped("dueamount_line_ids.amount")),
            sum(inv_line_ids.mapped("credit")) + sum(inv_line_ids.mapped("debit")),
        )
        # todo add a dueamount line
        # todo remove a dueamount line created by default
