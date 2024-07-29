# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase
from odoo import fields
from odoo.tools.date_utils import relativedelta


class TestMisBuilderCashflowPurchase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_model = cls.env['res.users'].with_context(no_reset_password=True)
        cls.vendor = cls.env.ref('base.res_partner_3')
        cls.product = cls.env.ref('product.product_delivery_01')
        cls.product1 = cls.env.ref('product.product_delivery_02')
        cls.payment_term_2rate = cls.env['account.payment.term'].create({
            'name': 'Payment term 30/60 end of month',
            'line_ids': [
                (0, 0, {
                    'value': 'percent',
                    'value_amount': 50,
                    'days': 30,
                }),
                (0, 0, {
                    'value': 'balance',
                    'days': 30,
                    'option': 'after_invoice_month'
                })
            ],
        })
        cls.account_liquidity = cls.env['account.account'].create({
            'name': 'Bank',
            'code': '100999',
            'user_type_id': cls.env.ref('account.data_account_type_liquidity').id,
        })
        cls.tax = cls.env['account.tax'].create({
            'name': 'Tax 22.0',
            'description': '22p',
            'amount': 22.0,
            'type_tax_use': 'purchase',
        })

    def _create_purchase_order_line(self, order, product, qty, price_unit, date):
        vals = {
            'name': product.name,
            'order_id': order.id,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'product_qty': qty,
            'price_unit': price_unit,
            'date_planned': date,
            'taxes_id': self.tax.id,
        }
        line = self.env['purchase.order.line'].create(vals)
        line.onchange_product_id()
        line._convert_to_write(line._cache)
        return line

    def test_01_purchase_no_payment_term_cashflow(self):
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
        })
        self._create_purchase_order_line(
            purchase_order, self.product, 5.0, 13,
            fields.Date.today() + relativedelta(days=40))
        self._create_purchase_order_line(
            purchase_order, self.product1, 5.0, 19,
            fields.Date.today() + relativedelta(days=70))
        self.assertEqual(
            len(purchase_order.order_line), 2, msg='Order line was not created')
        purchase_order.button_confirm()
        po_lines = purchase_order.order_line.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(len(po_lines), 1)
        for line in po_lines:
            self.assertTrue(line.cashflow_line_ids)
            self.assertAlmostEqual(
                sum(line.mapped('cashflow_line_ids.purchase_balance_forecast')),
                - line.price_total)

    def test_02_purchase_payment_term_2rate_cashflow(self):
        purchase_order1 = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'payment_term_id': self.payment_term_2rate.id,
        })
        self._create_purchase_order_line(
            purchase_order1, self.product, 5.0, 13,
            fields.Date.today() + relativedelta(days=40))
        self._create_purchase_order_line(
            purchase_order1, self.product1, 5.0, 19,
            fields.Date.today() + relativedelta(days=70))
        self.assertEqual(
            len(purchase_order1.order_line), 2, msg='Order line was not created')
        purchase_order1.button_confirm()
        po1_lines = purchase_order1.order_line.filtered(
            lambda x: x.product_id == self.product
        )
        self.assertEqual(len(po1_lines), 1)
        for line in po1_lines:
            self.assertEqual(len(line.cashflow_line_ids), 2)
            self.assertAlmostEqual(
                sum(line.mapped('cashflow_line_ids.purchase_balance_forecast')),
                - line.price_total)

        purchase_order1.button_cancel()
        self.assertFalse(purchase_order1.mapped("order_line.cashflow_line_ids"))
        purchase_order1.button_draft()
        self.assertTrue(purchase_order1.mapped("order_line.cashflow_line_ids"))
