from odoo import fields
from odoo.tests import Form, new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderConfirmationDate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_1")
        cls.product1 = cls.env.ref("product.product_product_2")
        cls.sale_user = new_test_user(
            cls.env,
            login="demo user",
            email="demo@email.it",
            groups="sales_team.group_sale_salesman",
        )

    def test_00_order_confirmation_date(self):
        sale_order_form = Form(self.sale_order_model.with_user(self.sale_user))
        sale_order_form.partner_id = self.partner
        sale_order_form.date_order = fields.Datetime.now()
        with sale_order_form.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 5
            line.price_unit = 100
        with sale_order_form.order_line.new() as line:
            line.product_id = self.product1
            line.product_uom_qty = 20
            line.price_unit = 100
        new_sale = sale_order_form.save()
        new_sale.action_confirm()
