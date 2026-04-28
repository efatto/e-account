from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form
from odoo.tools.date_utils import relativedelta

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderConfirmationDate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.user_model = cls.env["res.users"].with_context(no_reset_password=True)
        cls.group_sale = cls.env.ref("sales_team.group_sale_salesman")
        cls.sale_user = cls.user_model.create(
            [
                {
                    "name": "Demo user",
                    "login": "demo user",
                    "email": "demo@email.it",
                    "groups_id": [
                        (4, cls.env.ref("sales_team.group_sale_salesman").id),
                    ],
                }
            ]
        )

    def _create_sale_order_line(self, order, product, qty):
        order_form = Form(
            order.with_user(self.sale_user),
        )
        with order_form.order_line.new() as line_form:
            line_form.product_id = product
            line_form.product_uom_qty = qty
            line_form.price_unit = 100
        order_form.save()

    def test_00_order_confirmation_date(self):
        with freeze_time("2026-05-01 12:00:00"):
            date_order = fields.Datetime.now()
            sale_order_form = Form(self.sale_order_model.with_user(self.sale_user))
            sale_order_form.partner_id = self.partner
            sale_order_1 = sale_order_form.save()
            self._create_sale_order_line(sale_order_1, self.product, 5)
        with freeze_time("2026-05-11 12:00:00"):
            confirmation_date = sale_order_1.date_order + relativedelta(days=10)
            sale_order_1.action_confirm()
            self.assertEqual(sale_order_1.date_order, date_order)
            self.assertEqual(
                sale_order_1.confirmation_date.replace(
                    minute=0, second=0, microsecond=0
                ),
                confirmation_date.replace(minute=0, second=0, microsecond=0),
            )
