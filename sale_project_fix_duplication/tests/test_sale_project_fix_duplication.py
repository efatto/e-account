# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, common


class TestSaleOrderAnalyticAll(common.SavepointCase):
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

    def _create_sale_order_with_project(self):
        sale_form = Form(self.sale_order_model.with_user(self.sale_user))
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product
            order_line_form.product_uom_qty = 5
            order_line_form.price_unit = 100
        with sale_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product1
            order_line_form.product_uom_qty = 20
            order_line_form.price_unit = 100
        sale_order = sale_form.save()
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")
        project = self.env["project.project"].search([("name", "=", sale_order.name)])
        self.assertEqual(len(project), 1, msg="Project was not created")

    def test_01_order_create_task(self):
        task_type_new_id = self.env["project.task.type"].search([("name", "=", "New")])
        self.assertEqual(len(task_type_new_id), 1)
        self._create_sale_order_with_project()
        # create another sale order with project
        self._create_sale_order_with_project()
        task_type_new_id = self.env["project.task.type"].search([("name", "=", "New")])
        self.assertEqual(len(task_type_new_id), 1)
