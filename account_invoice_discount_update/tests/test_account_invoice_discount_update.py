from odoo import fields
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDiscountUpdate(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
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
                "code": "TEST.REVENUE",
                "name": "Sale revenue",
                "account_type": "income",
            }
        )
        self.expense_account = self.env["account.account"].create(
            {
                "code": "TEST.EXPENSE",
                "name": "Purchase expense",
                "account_type": "expense",
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner",
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
        # create invoice with a discount in line and check that it is updated
        invoice = self.create_custom_invoice(move_type)
        self.assertEqual(set(invoice.invoice_line_ids.mapped("discount")), {10})
        invoice.discount = 20
        invoice.invoice_discount_update()
        self.assertEqual(set(invoice.invoice_line_ids.mapped("discount")), {20})
        invoice._post()
        invoice.button_draft()
        self.assertEqual(set(invoice.invoice_line_ids.mapped("discount")), {20})
        self.assertEqual(invoice.state, "draft")
        invoice._post()
        self.assertEqual(set(invoice.invoice_line_ids.mapped("discount")), {20})
