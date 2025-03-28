from odoo.tests import common, Form


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

    def test_order_add_task_product(self):
        sale_form = Form(
            self.env["sale.order"].sudo(self.sale_user)
        )
        sale_form.partner_id = self.partner
        sale_order_1 = sale_form.save()
        # confirm order without lines
        sale_order_1.action_confirm()
        self.assertEqual(sale_order_1.state, 'sale')
        # check analytic account and project are created and are unique
        analytic = self.env['account.analytic.account'].search([
            ('name', '=', sale_order_1.name)
        ])
        self.assertEqual(len(analytic), 1, msg="Contract was not created")

        project = self.env['project.project'].search([
            ('name', '=', sale_order_1.name)
        ])
        self.assertEqual(len(project), 1, msg="Project was not created")
        # sale_form = Form(sale_order_1.sudo(self.sale_user))
        # with sale_form.order_line.new() as order_line_form:
        #     order_line_form.product_id = self.product
        #     order_line_form.product_uom_qty = 5
        #     order_line_form.price_unit = 100
        # with sale_form.order_line.new() as order_line_form:
        #     order_line_form.product_id = self.product1
        #     order_line_form.product_uom_qty = 20
        #     order_line_form.price_unit = 100
        # sale_order = sale_form.save()
        # # check new lines of type task and service tracking has the
        # # project of sale order
        # sol1 = sale_order.order_line[0]
        # sol2 = sale_order.order_line[1]
        # self.assertNotEqual(self.product1.service_tracking, "no")
        # self.assertEqual(sale_order_1.project_id, sol1.project_id)
        # self.assertEqual(sol1.project_id.sale_line_id, sol1)
        # self.assertEqual(sale_order_1.project_id, sol2.project_id)
        # self.assertEqual(len(sale_order_1.tasks_ids), 1)
