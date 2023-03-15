from odoo.tests import common


class TestSaleOrderAnalyticAll(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env['sale.order']
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.product = cls.env.ref('product.product_product_1')
        cls.product.service_tracking = "task_new_project"
        cls.product1 = cls.env.ref('product.product_product_2')
        cls.user_model = cls.env['res.users'].with_context(no_reset_password=True)
        cls.group_sale = cls.env.ref('sales_team.group_sale_salesman')
        cls.sale_user = cls.user_model.create([{
            'name': 'Demo user',
            'login': 'demo user',
            'email': 'demo@email.it',
            'groups_id': [
                (4, cls.env.ref('sales_team.group_sale_salesman').id),
            ]
        }])

    def _create_sale_order(self):
        new_sale = self.sale_order_model.sudo(self.sale_user).create({
            'partner_id': self.partner.id,
        })
        return new_sale

    def _create_sale_order_line(self, order, product, qty):
        line = self.env['sale.order.line'].sudo(self.sale_user).create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': qty,
            'price_unit': 100,
            })
        line.product_id_change()
        line._convert_to_write(line._cache)
        return line

    def test_order_add_task_product(self):
        sale_order_1 = self._create_sale_order()
        # confirm order without lines
        sale_order_1.action_confirm()
        self.assertEqual(sale_order_1.state, 'sale')
        # check project is created
        self.assertTrue(sale_order_1.project_id)
        sol1 = self._create_sale_order_line(sale_order_1, self.product, 5)
        sol2 = self._create_sale_order_line(sale_order_1, self.product1, 20)
        # check new lines of type task and service tracking has the
        # project of sale order
        self.assertNotEqual(self.product1.service_tracking, "no")
        self.assertEqual(sale_order_1.project_id, sol1.project_id)
        self.assertEqual(sol1.project_id.sale_line_id, sol1)
        self.assertEqual(sale_order_1.project_id, sol2.project_id)
        self.assertEqual(len(sale_order_1.tasks_ids), 1)
