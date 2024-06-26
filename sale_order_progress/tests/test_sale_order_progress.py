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

    def test_00_order(self):
        sale_form = Form(
            self.env["sale.order"].sudo(self.sale_user)
        )
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product
            order_line_form.product_uom_qty = 5.0
            order_line_form.price_unit = 100.0
            order_line_form.commitment_date = fields.Datetime.now() + relativedelta(
                days=40
            )
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product1
            order_line_form.product_uom_qty = 2.0
            order_line_form.price_unit = 200.0
            order_line_form.commitment_date = fields.Datetime.now() + relativedelta(
                days=70
            )
        sale_order = sale_form.save()
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, 'sale')
        # todo create deposit invoice and check deposit percent
