from odoo.tests import common
from odoo import fields
from odoo.tools.date_utils import relativedelta


class TestSaleOrderConfirmationDate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_1")
        cls.product.service_tracking = "task_in_project"
        cls.product1 = cls.env.ref("product.product_product_2")
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

    def _create_sale_order(self, date_order):
        new_sale = self.sale_order_model.with_user(self.sale_user).create(
            {
                "partner_id": self.partner.id,
                "date_order": date_order,
            }
        )
        return new_sale

    def _create_sale_order_line(self, order, product, qty):
        line = (
            self.env["sale.order.line"]
            .with_user(self.sale_user)
            .create(
                {
                    "order_id": order.id,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "price_unit": 100,
                }
            )
        )
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def test_00_order_confirmation_date(self):
        confirmation_date = fields.Datetime.now()
        date_order = confirmation_date + relativedelta(days=-10)
        sale_order_1 = self._create_sale_order(date_order)
        self._create_sale_order_line(sale_order_1, self.product, 5)
        self._create_sale_order_line(sale_order_1, self.product1, 20)
        self.assertEqual(sale_order_1.date_order, date_order)
        sale_order_1.action_confirm()
        self.assertEqual(sale_order_1.date_order, date_order)
        self.assertEqual(
            sale_order_1.confirmation_date.replace(minute=0, second=0, microsecond=0),
            confirmation_date.replace(minute=0, second=0, microsecond=0))
