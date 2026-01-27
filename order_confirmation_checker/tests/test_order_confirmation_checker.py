from odoo.tests import Form, SavepointCase


class TestProductMarginExclude(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_4")
        cls.product1 = cls.env.ref("product.product_product_3")
        cls.customerinfo_model = cls.env["product.customerinfo"]
        cls.customerinfo = cls.customerinfo_model.create(
            {
                "name": cls.partner.id,
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                # "product_id": cls.product.id,
                "product_code": "CUST1234",
            }
        )
        cls.extracted_text = """
# MyCompany\n\nMyCompany Srl\nVia Kimm 62\n22222 Varano (MI)\nSDI:
 MyCompanyinvoices@pec.it\nVAT: IT99999999999\nFiscal Code: 99999999999\nQuality
 system certified ISO 9001\n\nBILLING ADDRESS:\nVia Kimm 62\n22222 Varano
 (MI)\nCONTACTS:\nPhone: 0345465454\nEmail: info@MyCompany.com\n\nDATE:
 19/01/2026\nORDER: SO/2026/00287\nPAG.: 1/1\n\nPARTNER:\nMyCoa-Comp A/S\nBuonasr
 30, Skive DK-7800, Denmark\n+45 142828\nVAT: DK30303003\n\nCustomer ref.:\n50244
 - BT\n\nPayment terms: MT60\nBANK Fineco\nOutside SEPA circuit \n\n|  Description
 | Qty | U.M. | Amount | Total  |\n| --- | --- | --- | --- | --- |\n|  Order ref.
 SO/2026/03287 - 2/01/2026 50364 - BT |  |  |  |   |\n|  [PPC140226_HY-MyCoop] [1091160]
 PPC140226_HY-MyCoop PPC-UR-R1,5-L-V200-G-G-P01-RETURN-KIT-2,5A+V100 Assembled & tested
 | 3.000 | Unit(s) | 11.95000 | 35.85 €  |\n|  [PP2413424_HY-MyCoop] [125475]
 CUST1234MyCoop PPC-UR-R1,5-L-V200-G-G-P01-RETURN-KIT-2,5A+V100 Assembled & tested
 | 7.000 | Unit(s) | 16.98000 | 118.86 €  |\n|  [FURN_0096] Test product internal -
 PPCCBokin charge technical amusement park in offer | 1.000 | Unit(s) | 5.73000 | 5.73 €
 |\n|   | Total Without Taxes |   |   | 446.58 €  |\n|   | Taxes on 446.58 € |   |
 | 0.00 €  |\n|   | Total |   |   | 446.58 €  |\n\nScheduled Delivery Date:
 16/04/2026\n\nApplies the general conditions of sale. If confirmed after 3 days,
 50.00 Eur will be charged as a management cost to reprocess the order from the
 beginning."""

    def test_extract_text(self):
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        order = sale_order_form.save()
        # todo create pdf to attach and test
        # order.attachment_to_check_id
        content = self.extracted_text
        products = order._get_products_from_content(content)
        self.assertTrue(products, "No products found in content")
        self.assertIn(
            {"default_code": self.product.default_code, "id": self.product.id},
            products,
        )
        self.assertIn(
            {"default_code": self.product1.default_code, "id": self.product1.id},
            products,
        )
