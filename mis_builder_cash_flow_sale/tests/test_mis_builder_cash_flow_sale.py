# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import Form, SavepointCase
from odoo.tools.date_utils import relativedelta


class TestMisBuilderCashflowSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.customer = cls.env.ref("base.res_partner_3")
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.product1 = cls.env.ref("product.product_delivery_02")
        cls.company = cls.env.ref("base.main_company")
        cls.payment_mode_model = cls.env["account.payment.mode"]
        cls.journal_model = cls.env["account.journal"]
        cls.manual_in = cls.env.ref("account.account_payment_method_manual_in")
        cls.manual_in.bank_account_required = True
        cls.journal_c1 = cls.journal_model.create(
            {
                "name": "J1",
                "code": "J1",
                "type": "bank",
                "company_id": cls.company.id,
                "bank_acc_number": "123456",
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
                            "option": "after_invoice_month",
                        },
                    ),
                ],
            }
        )
        cls.account_liquidity = cls.env["account.account"].create(
            {
                "name": "Bank",
                "code": "100999",
                "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
            }
        )
        cls.customer_payment_mode = cls.payment_mode_model.create(
            {
                "name": "Customers Bank Payment",
                "bank_account_link": "fixed",
                "payment_method_id": cls.manual_in.id,
                "show_bank_account_from_journal": True,
                "company_id": cls.company.id,
                "fixed_journal_id": cls.journal_c1.id,
            }
        )

    def test_01_sale_no_payment_term_cashflow(self):
        sale_form = Form(
            self.env["sale.order"].with_context(test_mis_builder_cash_flow_sale=True)
        )
        sale_form.partner_id = self.customer
        sale_form.payment_mode_id = self.customer_payment_mode
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product
            order_line_form.product_uom_qty = 5.0
            order_line_form.price_unit = 13.0
            order_line_form.commitment_date = fields.Datetime.now() + relativedelta(
                days=40
            )
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product1
            order_line_form.product_uom_qty = 5.0
            order_line_form.price_unit = 19.0
            order_line_form.commitment_date = fields.Datetime.now() + relativedelta(
                days=70
            )
        sale_order = sale_form.save()
        self.assertEqual(
            len(sale_order.order_line), 2, msg="Order line was not created"
        )
        sale_order.action_confirm()
        so_lines = sale_order.order_line.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(len(so_lines), 1)
        for line in so_lines:
            self.assertTrue(line.cashflow_line_ids)
            self.assertAlmostEqual(
                sum(line.mapped("cashflow_line_ids.sale_balance_forecast")),
                line.price_total,
            )

    def test_02_sale_payment_term_2rate_cashflow(self):
        sale_form = Form(
            self.env["sale.order"].with_context(test_mis_builder_cash_flow_sale=True)
        )
        sale_form.partner_id = self.customer
        sale_form.payment_term_id = self.payment_term_2rate
        sale_form.payment_mode_id = self.customer_payment_mode
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product
            order_line_form.product_uom_qty = 5.0
            order_line_form.price_unit = 13.0
            order_line_form.commitment_date = fields.Datetime.now() + relativedelta(
                days=40
            )
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product1
            order_line_form.product_uom_qty = 5.0
            order_line_form.price_unit = 19.0
            order_line_form.commitment_date = fields.Datetime.now() + relativedelta(
                days=70
            )
        sale_order = sale_form.save()
        self.assertEqual(
            len(sale_order.order_line), 2, msg="Order line was not created"
        )
        sale_order.action_confirm()
        so_lines = sale_order.order_line.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(len(so_lines), 1)
        for line in so_lines:
            self.assertEqual(len(line.cashflow_line_ids), 2)
            self.assertAlmostEqual(
                sum(line.mapped("cashflow_line_ids.sale_balance_forecast")),
                line.price_total,
            )

        sale_order.action_cancel()
        self.assertFalse(sale_order.mapped("order_line.cashflow_line_ids"))
        sale_order.action_draft()
        self.assertTrue(sale_order.mapped("order_line.cashflow_line_ids"))
