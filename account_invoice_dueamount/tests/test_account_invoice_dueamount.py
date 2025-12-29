from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDueAmount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.today = fields.Date.today()
        cls.sale_journal = (
            cls.env["account.journal"]
            .with_company(cls.env.user.company_id.id)
            .search(
                [
                    ("type", "=", "sale"),
                ],
                limit=1,
            )
        )
        cls.purchase_journal = (
            cls.env["account.journal"]
            .with_company(cls.env.user.company_id.id)
            .search(
                [
                    ("type", "=", "purchase"),
                ],
                limit=1,
            )
        )
        cls.revenue_account = cls.env["account.account"].create(
            {
                "code": "TEST.REVENUE",
                "name": "Sale revenue",
                "account_type": "income",
            }
        )
        cls.expense_account = cls.env["account.account"].create(
            {
                "code": "TEST.EXPENSE",
                "name": "Purchase expense",
                "account_type": "expense",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.payment_term_2rate = cls.env["account.payment.term"].create(
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
                            "end_month": True,
                        },
                    ),
                ],
            }
        )

    def create_custom_invoice(self, move_type):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type=move_type)
        )
        invoice_form.invoice_date = fields.Date.today()
        invoice_form.currency_id = self.env.ref("base.EUR")
        invoice_form.journal_id = (
            self.sale_journal if move_type.startswith("out_") else self.purchase_journal
        )
        invoice_form.company_id = self.env.user.company_id
        invoice_form.partner_id = self.partner
        invoice_form.invoice_payment_term_id = self.payment_term_2rate
        for _i in range(0, 3):
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.env.ref("product.product_product_5")
                line_form.quantity = 5
                line_form.account_id = (
                    self.revenue_account
                    if move_type.startswith("out_")
                    else self.expense_account
                )
                line_form.name = "product test 5"
                line_form.price_unit = 6
                line_form.discount = 10
                line_form.currency_id = self.env.ref("base.EUR")
        invoice = invoice_form.save()
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
        invoice = self.create_custom_invoice(move_type)
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
            lambda x: x.account_id.account_type
            in ("asset_receivable", "liability_payable")
        )
        self.assertAlmostEqual(
            sum(invoice.mapped("dueamount_line_ids.amount")),
            sum(inv_line_ids.mapped("credit")) + sum(inv_line_ids.mapped("debit")),
        )
        # todo add a dueamount line
        # todo remove a dueamount line created by default
