from odoo.tests import common


class TestSaleOrderRevision(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env['sale.order']
        cls.partner_id = cls.env.ref('base.res_partner_2').id
        cls.project_product = cls.env['product.product'].create({
            'name': 'Service creating task on task delivered',
            'service_policy': 'delivered_timesheet',
            'service_tracking': 'task_new_project',
            'type': 'service',
            'uom_id': cls.env.ref('uom.product_uom_hour').id,
            'uom_po_id': cls.env.ref('uom.product_uom_hour').id,
            'list_price': 50.0,
        })

    def _create_sale_order(self):
        # Creating a sale order
        new_sale = self.sale_order_model.create({
            'partner_id': self.partner_id,
            'order_line': [(0, 0, {
                'product_id': self.project_product.id,
                'product_uom_qty': '15.0'
            })]
        })
        return new_sale

    @staticmethod
    def _revision_sale_order(sale_order):
        # Cancel the sale order
        sale_order.action_cancel()
        # Create a new revision
        return sale_order.create_revision()

    def test_00_order_revision(self):
        """Check revision process"""
        # Create a Sale Order
        sale_order_1 = self._create_sale_order()
        sale_order_1.action_confirm()
        # check analytic account is created
        self.assertTrue(sale_order_1.analytic_account_id)
        # Create a revision of the Sale Order
        self._revision_sale_order(sale_order_1)
        # check analytic account is the same
        revision = sale_order_1.current_revision_id
        self.assertEqual(sale_order_1.analytic_account_id,
                         revision.analytic_account_id)
