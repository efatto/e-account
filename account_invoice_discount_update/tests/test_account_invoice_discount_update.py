from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDueAmount(AccountTestInvoicingCommon):
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
        invoice_line_data = {
            "product_id": self.env.ref("product.product_product_5").id,
            "quantity": 5,
            "account_id": move_type.startswith("out_")
            and self.revenue_account.id
            or self.expense_account.id,
            "name": "product test 5",
            "price_unit": 6,
            "discount": 10,
            "currency_id": self.env.ref("base.EUR").id,
        }
        invoice_line_datas = []
        for _i in range(0, 3):
            invoice_line_datas.append((0, 0, invoice_line_data))
        invoice = self.env["account.move"].create(
            {
                "move_type": move_type,
                "invoice_date": fields.Date.today(),
                "currency_id": self.env.ref("base.EUR").id,
                "journal_id": move_type.startswith("out_")
                and self.sale_journal.id
                or self.purchase_journal.id,
                "company_id": self.env.user.company_id.id,
                "partner_id": self.partner.id,
                "invoice_line_ids": invoice_line_datas,
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
