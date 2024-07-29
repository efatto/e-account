from odoo import fields
from odoo.tests import common, Form
from odoo.tools.date_utils import relativedelta


class TestSaleOrderProgress(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env['sale.order']
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.product1 = cls.env.ref("product.product_delivery_02")
        cls.user_model = cls.env['res.users'].with_context(no_reset_password=True)
        cls.group_sale = cls.env.ref('sales_team.group_sale_salesman')
        cls.sale_user = cls.user_model.create([{
            'name': 'Demo user',
            'login': 'demo user',
            'email': 'demo@email.it',
            'groups_id': [
                (4, cls.group_sale.id),
            ]
        }])
        cls.tax = cls.env['account.tax'].create({
            'name': 'Tax 22.0',
            'description': '22',
            'amount': 22.0,
            'type_tax_use': 'sale',
        })

    def test_00_order(self):
        sale_form = Form(
            self.env["sale.order"].sudo(self.sale_user)
        )
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product
            order_line_form.product_uom_qty = 5.0
            order_line_form.price_unit = 100.0
            order_line_form.tax_id.add(self.tax)
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product1
            order_line_form.product_uom_qty = 2.0
            order_line_form.price_unit = 200.0
            order_line_form.tax_id.add(self.tax)
        sale_order = sale_form.save()
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, 'sale')
        self.assertAlmostEqual(
            sale_order.amount_total,
            (500 + 400) * 1.22,
            places=2,
        )
        # todo create deposit invoice and check deposit percent
        sale_form = Form(sale_order)
        with sale_form.order_progress_ids.new() as order_progress_form:
            order_progress_form.name = "Advance 10%"
            order_progress_form.offset_month = 1
            order_progress_form.amount_percent = 10
        with sale_form.order_progress_ids.new() as order_progress_form:
            order_progress_form.name = "First SAL"
            order_progress_form.offset_month = 3
            order_progress_form.amount_percent = 60
        with sale_form.order_progress_ids.new() as order_progress_form:
            order_progress_form.name = "Last SAL"
            order_progress_form.offset_month = 4
            order_progress_form.amount_percent = 30
        sale_order = sale_form.save()
        sop_lines = sale_order.order_progress_ids
        self.assertEqual(len(sop_lines), 3)
        self.assertAlmostEqual(
            sum(sop_lines.mapped("amount_toinvoice")),
            sale_order.amount_total, places=2)
