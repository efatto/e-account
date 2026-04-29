from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDiscountUpdate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_journal = cls.company_data["default_journal_sale"]
        cls.purchase_journal = cls.company_data["default_journal_purchase"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.product = cls._create_product(lst_price=100, taxes_id=cls.tax_sale_a)

    def create_custom_invoice(self, move_type):
        invoice = self._create_invoice(
            move_type=move_type,
            journal_id=self.sale_journal
            if move_type.startswith("out_")
            else self.purchase_journal,
            post=False,
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
