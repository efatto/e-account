from odoo.tests import SavepointCase


class TestProductMarginExclude(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env['sale.order']
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.product = cls.env.ref('product.product_product_1')
        cls.product_exclude = cls.env['product.product'].create({
            'name': 'Product excluded from margin',
            'exclude_from_margin': True,
        })

    def test_01_product_margin_exclude(self):
        sale_order = self.sale_order_model.create({
            'name': 'Test_SO_EXCL',
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'purchase_price': 45.0,
                    'price_unit': 100.0,
                    'product_uom': self.product.uom_id.id,
                    'product_uom_qty': 10.0,
                    'product_id': self.product.id,
                }),
            ],
            'partner_id': self.partner.id,
            })

        # (10 * 100) - (10 * 45) = 550 margin / (10 * 100) = 55%
        self.assertEqual(sale_order.percent, 55.00)

        sale_order.write({
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'purchase_price': 45.0,
                    'price_unit': 100.0,
                    'product_uom': self.product_exclude.uom_id.id,
                    'product_uom_qty': 10.0,
                    'product_id': self.product_exclude.id,
                }),
            ],
        })
        self.assertEqual(sale_order.amount_untaxed, 2000.0)
        self.assertEqual(sale_order.percent, 55.00)
