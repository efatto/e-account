from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDueAmount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.sale_journal = cls.company_data["default_journal_sale"]
        cls.purchase_journal = cls.company_data["default_journal_purchase"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.product = cls._create_product(lst_price=100, taxes_id=cls.tax_sale_a)
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
                            "delay_type": "days_after",
                            "nb_days": 30,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "value": "percent",
                            "value_amount": 50,
                            "delay_type": "days_after_end_of_next_month",
                        },
                    ),
                ],
            }
        )

    def create_custom_invoice(self, move_type):
        invoice = self._create_invoice(
            move_type=move_type,
            journal_id=self.sale_journal
            if move_type.startswith("out_")
            else self.purchase_journal,
            post=False,
            invoice_payment_term_id=self.payment_term_2rate,
            invoice_line_ids=[
                self._prepare_invoice_line(
                    product_id=self.product,
                    quantity=5.0,
                    partner_id=self.partner,
                    price_unit=6,
                    discount=10,
                )
                for _i in range(0, 3)
            ],
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
