# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields
from odoo.tests import Form, new_test_user, tagged, users

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestDeliveryAutoRefresh(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.test_user = new_test_user(
            cls.env,
            login="test_user",
            groups="account.group_account_invoice,"
            "account.group_delivery_invoice_address,"
            "sales_team.group_sale_salesman,"
            "stock.group_stock_manager",
        )
        cls.revenue_account = cls.env["account.account"].create(
            {
                "code": "TEST.REVENUE",
                "name": "Sale revenue",
                "account_type": "income",
            }
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Service Test",
                "type": "service",
                "property_account_income_id": cls.revenue_account.id,
            }
        )
        pricelist = cls.env["product.pricelist"].create(
            {"name": "Test pricelist", "currency_id": cls.env.company.currency_id.id}
        )
        carrier_form = Form(cls.env["delivery.carrier"])
        carrier_form.name = "Test carrier 1"
        carrier_form.delivery_type = "base_on_rule"
        carrier_form.product_id = cls.service
        with carrier_form.price_rule_ids.new() as price_rule_form:
            price_rule_form.variable = "weight"
            price_rule_form.operator = "<="
            price_rule_form.max_value = 20
            price_rule_form.list_base_price = 50
        with carrier_form.price_rule_ids.new() as price_rule_form:
            price_rule_form.variable = "weight"
            price_rule_form.operator = "<="
            price_rule_form.max_value = 40
            price_rule_form.list_base_price = 30
            price_rule_form.list_price = 1
            price_rule_form.variable_factor = "weight"
        with carrier_form.price_rule_ids.new() as price_rule_form:
            price_rule_form.variable = "weight"
            price_rule_form.operator = ">"
            price_rule_form.max_value = 40
            price_rule_form.list_base_price = 20
            price_rule_form.list_price = 1.5
            price_rule_form.variable_factor = "weight"
        cls.carrier_1 = carrier_form.save()
        carrier_form = Form(cls.env["delivery.carrier"])
        carrier_form.name = "Test carrier 2"
        carrier_form.delivery_type = "base_on_rule"
        carrier_form.product_id = cls.service
        with carrier_form.price_rule_ids.new() as price_rule_form:
            price_rule_form.variable = "weight"
            price_rule_form.operator = "<="
            price_rule_form.max_value = 20
            price_rule_form.list_base_price = 50
        cls.carrier_2 = carrier_form.save()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "weight": 10,
                "list_price": 20,
                "property_account_income_id": cls.revenue_account.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "property_delivery_carrier_id": cls.carrier_1.id,
                "property_product_pricelist": pricelist.id,
            }
        )
        cls.settings = cls.env["res.config.settings"].create({})
        cls.settings.sale_auto_add_delivery_line = False
        cls.settings.execute()
        order_form = Form(cls.env["sale.order"].with_user(cls.test_user))
        order_form.partner_id = cls.partner
        order_form.partner_invoice_id = cls.partner
        order_form.partner_shipping_id = cls.partner
        with order_form.order_line.new() as ol_form:
            ol_form.product_id = cls.product
            ol_form.product_uom_qty = 2
        cls.order = order_form.save()
        cls.order.carrier_id = cls.carrier_1

    @staticmethod
    def _create_invoice_from_so(order):
        picking = order.picking_ids[0]
        for ml in picking.move_ids:
            ml.quantity = ml.product_qty
        picking._action_done()
        order._create_invoices()
        invoice = order.invoice_ids[0]
        return invoice

    @users("test_user")
    def test_00_auto_refresh_invoice_from_so(self):
        self.assertFalse(self.order.order_line.filtered("is_delivery"))
        self.settings.sale_auto_add_delivery_line = True
        self.settings.execute()
        self.settings.sale_auto_void_delivery_line = True
        self.settings.execute()
        delivery_line = self._confirm_sale_order(self.order, 3)
        self.assertTrue(delivery_line.exists())
        invoice = self._create_invoice_from_so(self.order)
        self.assertEqual(invoice.delivery_carrier_id, self.order.carrier_id)
        delivery_line = invoice.line_ids.filtered("is_delivery")
        self.assertTrue(delivery_line.exists())
        sale_delivery_line = self.order.order_line.filtered("is_delivery")
        self.assertEqual(delivery_line.sale_line_ids, sale_delivery_line)
        self.assertAlmostEqual(delivery_line.price_unit, 60)
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.new() as new_il:
            new_il.product_id = self.product
            new_il.quantity = 2
        invoice = invoice_form.save()
        # check invoice delivery line in changed and with new price
        line_delivery = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(line_delivery.price_unit, 95)
        self.assertEqual(line_delivery, delivery_line)
        # Test saving the discount
        with Form(invoice) as invoice_form:
            lines_to_edit = [
                i
                for i, x in enumerate(invoice_form.invoice_line_ids._records)
                if x.get("product_id") == self.service.id
            ]
            with invoice_form.invoice_line_ids.edit(
                lines_to_edit[0]
            ) as line_delivery_form:
                line_delivery_form.discount = 10
        line_delivery = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(line_delivery.discount, 10)
        self.assertEqual(line_delivery, delivery_line)
        self.assertEqual(line_delivery.sale_line_ids, sale_delivery_line)
        invoice.delivery_carrier_id = self.carrier_2
        line_delivery = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(line_delivery.discount, 10)

    @staticmethod
    def _confirm_sale_order(order, qty):
        sale_form = Form(order)
        # Force the delivery line creation
        with sale_form.order_line.edit(0) as line_form:
            line_form.product_uom_qty = qty
        sale_form.save()
        line_delivery = order.order_line.filtered("is_delivery")
        order.action_confirm()
        return line_delivery

    def _test_autorefresh_unlink_line(self):
        """Helper method to test the possible cases for voiding the line"""
        self.assertFalse(self.order.order_line.filtered("is_delivery"))
        self.settings.sale_auto_add_delivery_line = True
        self.settings.execute()
        sale_form = Form(self.order)
        # Force the delivery line creation
        with sale_form.order_line.edit(0) as line_form:
            line_form.product_uom_qty = 2
        sale_form.save()
        return self.order.order_line.filtered("is_delivery")

    @users("test_user")
    def test_01_auto_refresh_so_and_unlink_line(self):
        """The return wasn't flagged to refund, so the delivered qty won't
        change, thus the delivery line shouldn't be either"""
        self._test_autorefresh_unlink_line()
        delivery_line = self.order.order_line.filtered("is_delivery")
        sale_form = Form(self.order)
        sale_form.order_line.remove(0)
        sale_form.save()
        self.assertFalse(delivery_line.exists())

    @users("test_user")
    def test_02_auto_add_delivery_line_all_services(self):
        self.settings.sale_auto_add_delivery_line = True
        self.settings.set_values()
        service = self.env["product.product"].create(
            {"name": "Service Test", "type": "service"}
        )
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = self.partner
        invoice_form.partner_shipping_id = self.partner
        invoice_form.delivery_carrier_id = self.carrier_1
        with invoice_form.invoice_line_ids.new() as il_form:
            il_form.product_id = service
            il_form.quantity = 2
        invoice = invoice_form.save()
        delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertFalse(delivery_line.exists())

    def _create_invoice(self, move_type="out_invoice", **values):
        vals = {
            "move_type": move_type,
            "partner_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "delivery_carrier_id": self.carrier_1.id,
            "invoice_date": fields.Date.to_date("2026-01-15"),
            "invoice_line_ids": [
                Command.create(
                    {
                        "product_id": self.product.id,
                        "quantity": 2,
                        "price_unit": 20,
                        "tax_ids": [Command.clear()],
                    }
                )
            ],
        }
        vals.update(values)
        return self.env["account.move"].create(vals)

    def _assert_balanced(self, invoice):
        self.assertTrue(
            invoice.company_currency_id.is_zero(sum(invoice.line_ids.mapped("balance")))
        )
        receivable = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertAlmostEqual(
            abs(sum(receivable.mapped("amount_currency"))), invoice.amount_total
        )

    def test_invoice_refresh_preserves_line_and_balances(self):
        self.env.company.sale_auto_add_delivery_line = True
        invoice = self._create_invoice()
        delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(delivery_line.price_unit, 50)
        self._assert_balanced(invoice)
        product_line = invoice.invoice_line_ids - delivery_line
        invoice.write(
            {"invoice_line_ids": [Command.update(product_line.id, {"quantity": 3})]}
        )
        self.assertEqual(
            invoice.invoice_line_ids.filtered("is_delivery"), delivery_line
        )
        self.assertEqual(delivery_line.price_unit, 60)
        self._assert_balanced(invoice)
        invoice.action_post()
        invoice.ref = "Posted invoice"
        self.assertEqual(delivery_line.price_unit, 60)
        self._assert_balanced(invoice)

    def test_remove_carrier_and_last_product(self):
        self.env.company.sale_auto_add_delivery_line = True
        invoice = self._create_invoice()
        invoice.delivery_carrier_id = False
        self.assertFalse(invoice.invoice_line_ids.filtered("is_delivery"))
        self._assert_balanced(invoice)
        invoice.delivery_carrier_id = self.carrier_1
        product_line = invoice.invoice_line_ids.filtered(
            lambda line: not line.is_delivery
        )
        invoice.write({"invoice_line_ids": [Command.delete(product_line.id)]})
        self.assertFalse(invoice.invoice_line_ids)
        self._assert_balanced(invoice)

    def test_disabled_refresh_preserves_imported_delivery(self):
        self.env.company.sale_auto_add_delivery_line = False
        invoice = self._create_invoice()
        delivery_line = invoice._create_delivery_line(self.carrier_1, 123)
        invoice.ref = "Do not refresh"
        self.assertEqual(
            invoice.invoice_line_ids.filtered("is_delivery"), delivery_line
        )
        self.assertEqual(delivery_line.price_unit, 123)
        self._assert_balanced(invoice)

    def test_batch_refresh_customer_documents_only(self):
        invoices = self.env["account.move"]
        for move_type in (
            "out_invoice",
            "out_refund",
            "out_receipt",
            "in_invoice",
            "in_refund",
        ):
            invoices |= self._create_invoice(move_type)
        self.env.company.sale_auto_add_delivery_line = True
        invoices.write({"ref": "Batch update"})
        for invoice in invoices:
            lines = invoice.invoice_line_ids.filtered("is_delivery")
            if invoice.is_sale_document(include_receipts=True):
                self.assertEqual(len(lines), 1)
                self.assertEqual(lines.price_unit, 50)
                self._assert_balanced(invoice)
            else:
                self.assertFalse(lines)

    def test_rule_margins(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.carrier_1.write({"margin": 0.1, "fixed_margin": 5})
        invoice = self._create_invoice()
        self.assertAlmostEqual(
            invoice.invoice_line_ids.filtered("is_delivery").price_unit, 60
        )

    def test_rules_include_services_in_amount(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.carrier_1.price_rule_ids.unlink()
        self.carrier_1.write(
            {
                "price_rule_ids": [
                    Command.create(
                        {
                            "variable": "price",
                            "operator": ">=",
                            "max_value": 100,
                            "list_base_price": 7,
                        }
                    )
                ]
            }
        )
        invoice = self._create_invoice()
        invoice.write(
            {
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.service.id,
                            "price_unit": 100,
                            "quantity": 1,
                            "tax_ids": [Command.clear()],
                        }
                    )
                ]
            }
        )
        self.assertEqual(invoice.invoice_line_ids.filtered("is_delivery").price_unit, 7)

    def test_weight_volume_rules(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.product.volume = 2
        self.carrier_1.price_rule_ids.unlink()
        self.carrier_1.write(
            {
                "price_rule_ids": [
                    Command.create(
                        {
                            "variable": "wv",
                            "operator": ">=",
                            "max_value": 0,
                            "list_base_price": 0,
                            "list_price": 1,
                            "variable_factor": "wv",
                        }
                    )
                ]
            }
        )
        invoice = self._create_invoice()
        self.assertEqual(
            invoice.invoice_line_ids.filtered("is_delivery").price_unit, 40
        )

    def test_free_shipping_foreign_currency_and_refund(self):
        self.env.company.sale_auto_add_delivery_line = True
        foreign_currency = self.env["res.currency"].create(
            {
                "name": "XTS",
                "symbol": "T",
                "rounding": 0.01,
                "rate_ids": [
                    Command.create(
                        {
                            "name": "2026-01-01",
                            "rate": 2,
                            "company_id": self.env.company.id,
                        }
                    )
                ],
            }
        )
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.env.company.currency_id.id,
                "company_id": self.env.company.id,
                "name": "2026-01-01",
                "rate": 1,
            }
        )
        pricelist = self.env["product.pricelist"].create(
            {"name": "Foreign", "currency_id": foreign_currency.id}
        )
        carrier = self.env["delivery.carrier"].create(
            {
                "name": "Fixed",
                "delivery_type": "fixed",
                "product_id": self.service.id,
                "fixed_price": 50,
                "free_over": True,
                "amount": 100,
                "margin": 0.5,
                "fixed_margin": 20,
            }
        )
        for move_type in ("out_invoice", "out_refund"):
            invoice = self._create_invoice(
                move_type,
                currency_id=foreign_currency.id,
                pricelist_id=pricelist.id,
                delivery_carrier_id=carrier.id,
            )
            delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
            self.assertAlmostEqual(delivery_line.price_unit, 100)
            product_line = invoice.invoice_line_ids - delivery_line
            invoice.write(
                {
                    "invoice_line_ids": [
                        Command.update(product_line.id, {"quantity": 10})
                    ]
                }
            )
            self.assertEqual(delivery_line.price_unit, 0)
            self._assert_balanced(invoice)

    def test_delivery_category_account_and_fiscal_position(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.service.property_account_income_id = False
        self.service.categ_id = self.env["product.category"].create(
            {
                "name": "Delivery",
                "property_account_income_categ_id": self.revenue_account.id,
            }
        )
        mapped_account = self.revenue_account.copy({"code": "TEST.MAPPED"})
        tax = self.env["account.tax"].create(
            {"name": "Shipping 10%", "amount": 10, "type_tax_use": "sale"}
        )
        mapped_tax = tax.copy({"name": "Shipping 20%", "amount": 20})
        self.service.taxes_id = tax
        position = self.env["account.fiscal.position"].create(
            {
                "name": "Shipping fiscal position",
                "account_ids": [
                    Command.create(
                        {
                            "account_src_id": self.revenue_account.id,
                            "account_dest_id": mapped_account.id,
                        }
                    )
                ],
                "tax_ids": [
                    Command.create({"tax_src_id": tax.id, "tax_dest_id": mapped_tax.id})
                ],
            }
        )
        invoice = self._create_invoice(fiscal_position_id=position.id)
        delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(delivery_line.account_id, mapped_account)
        self.assertEqual(delivery_line.tax_ids, mapped_tax)
        self.assertEqual(delivery_line.price_total, 60)
        self._assert_balanced(invoice)

    def test_grouped_invoices_keep_delivery_sales_links(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.product.invoice_policy = "order"
        second_order = self.order.copy()
        orders = self.order | second_order
        orders.action_confirm()
        sales_lines = orders.order_line.filtered("is_delivery")
        invoices = orders._create_invoices()
        self.assertEqual(len(invoices), 1)
        delivery_line = invoices.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(len(delivery_line), 1)
        self.assertEqual(delivery_line.sale_line_ids, sales_lines)
        self.assertEqual(delivery_line.price_unit, 70)
        self._assert_balanced(invoices)

    def test_different_carriers_create_separate_invoices(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.product.invoice_policy = "order"
        second_order = self.order.copy({"carrier_id": self.carrier_2.id})
        orders = self.order | second_order
        orders.action_confirm()
        invoices = orders._create_invoices()
        self.assertEqual(len(invoices), 2)
        self.assertEqual(invoices.delivery_carrier_id, self.carrier_1 | self.carrier_2)

    def test_company_settings_are_respected_in_batch(self):
        second_company = self.setup_other_company()["company"]
        self.env.company.sale_auto_add_delivery_line = True
        second_company.sale_auto_add_delivery_line = False
        first = self._create_invoice()
        second = self._create_invoice(company_id=second_company.id)
        (first | second).write({"ref": "Multiple companies"})
        self.assertTrue(first.invoice_line_ids.filtered("is_delivery"))
        self.assertFalse(second.invoice_line_ids.filtered("is_delivery"))
        second_company.sale_auto_add_delivery_line = True
        second.ref = "Enable second company"
        self.assertEqual(second.invoice_line_ids.filtered("is_delivery").price_unit, 50)
        self._assert_balanced(first)
        self._assert_balanced(second)

    def test_product_catalog_refresh(self):
        self.env.company.sale_auto_add_delivery_line = True
        invoice = self._create_invoice()
        delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
        invoice._update_order_line_info(self.product.id, 3)
        self.assertEqual(delivery_line.price_unit, 60)
        self._assert_balanced(invoice)
        invoice._update_order_line_info(self.product.id, 0)
        self.assertFalse(invoice.invoice_line_ids.filtered("is_delivery"))
        self._assert_balanced(invoice)

    def test_pricelist_update_preserves_delivery(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.carrier_1.price_rule_ids.unlink()
        self.carrier_1.price_rule_ids = [
            Command.create(
                {
                    "variable": "price",
                    "operator": "<",
                    "max_value": 100,
                    "list_base_price": 50,
                }
            ),
            Command.create(
                {
                    "variable": "price",
                    "operator": ">=",
                    "max_value": 100,
                    "list_base_price": 7,
                }
            ),
        ]
        invoice = self._create_invoice()
        delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(delivery_line.price_unit, 50)
        delivery_line.discount = 10
        self.product.list_price = 100
        invoice.button_update_prices_from_pricelist()
        self.assertEqual(delivery_line.price_unit, 7)
        self.assertEqual(delivery_line.discount, 10)
        self._assert_balanced(invoice)

    def test_fixed_price_without_pricelist(self):
        self.env.company.sale_auto_add_delivery_line = True
        carrier = self.env["delivery.carrier"].create(
            {
                "name": "Fixed",
                "delivery_type": "fixed",
                "product_id": self.service.id,
                "fixed_price": 25,
            }
        )
        invoice = self._create_invoice(
            pricelist_id=False, delivery_carrier_id=carrier.id
        )
        self.assertEqual(
            invoice.invoice_line_ids.filtered("is_delivery").price_unit, 25
        )

    def test_real_policy_does_not_zero_invoice_charge(self):
        self.env.company.sale_auto_add_delivery_line = True
        self.carrier_1.invoice_policy = "real"
        invoice = self._create_invoice()
        delivery_line = invoice.invoice_line_ids.filtered("is_delivery")
        self.assertEqual(delivery_line.price_unit, 50)
        self.assertNotIn("Estimated Cost", delivery_line.name)
