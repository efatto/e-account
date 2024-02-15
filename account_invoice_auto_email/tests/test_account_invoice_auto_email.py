
from odoo.tests import common, Form
from datetime import datetime


class TestAccountInvoiceAutoEmail(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.partner_01 = cls.env.ref("base.res_partner_10")
        cls.partner_02 = cls.env.ref("base.res_partner_address_17")
        cls.account_payment_term = cls.env.ref(
            "account.account_payment_term_end_following_month"
        )
        cls.account_payment_term.fatturapa_pt_id = cls.env.ref(
            "l10n_it_fiscal_payment_term.fatturapa_tp02"
        )
        cls.account_payment_term.fatturapa_pm_id = cls.env.ref(
            "l10n_it_fiscal_payment_term.fatturapa_mp05"
        )
        cls.product = cls.env.ref("product.product_product_1")
        cls.group_accounting = cls.env.ref("account.group_account_user")
        cls.account_user = cls.env["res.users"].create(
            [
                {
                    "name": "Accounting user",
                    "login": "account user",
                    "email": "account@email.it",
                    "groups_id": [
                        (4, cls.group_accounting.id),
                    ],
                }
            ]
        )

    def test_00_send_email_auto(self):
        date = datetime.today()
        invoice_form = Form(
            self.env["account.move"].with_user(self.account_user).with_context(
                check_move_validity=False,
                company_id=self.account_user.company_id.id,
                default_move_type="out_invoice",
            )
        )
        invoice_form.date = date
        invoice_form.invoice_date = date
        invoice_form.partner_id = self.env.ref("base.res_partner_2")
        invoice_form.journal_id = self.env["account.journal"].search([
            ("type", "=", "sale")
        ], limit=1)[0]
        invoice_form.invoice_payment_term_id = self.account_payment_term
        with invoice_form.invoice_line_ids.new() as invoice_line_form:
            invoice_line_form.product_id = self.product
            invoice_line_form.quantity = 1.0
            invoice_line_form.price_unit = 100.0
            invoice_line_form.name = "Test product"
            # invoice_line_form.account_id = self.account_expense
        invoice = invoice_form.save()
        invoice.action_open_export_send_sdi()
        self.assertIn(
            invoice.message_ids,
            "?"
        )
