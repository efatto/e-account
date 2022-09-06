from odoo import fields, models
from odoo.tools import float_round


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    rounding_method = fields.Selection(
        [("UP", "Up"),
         ("DOWN", "Down"),
         ("HALF-UP", "Half-up")],
        default="HALF-UP", string="Rounding method")

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        self.ensure_one()
        if self.price_round and self.rounding_method != 'HALF-UP':
            convert_to_price_uom = (
                lambda price: product.uom_id._compute_price(price, price_uom))
            # complete formula
            price_limit = price
            price = (price - (price * (self.price_discount / 100))) or 0.0
            if self.price_round:
                price = float_round(price, precision_rounding=self.price_round,
                                    rounding_method=self.rounding_method)

            if self.price_surcharge:
                price_surcharge = convert_to_price_uom(self.price_surcharge)
                price += price_surcharge

            if self.price_min_margin:
                price_min_margin = convert_to_price_uom(self.price_min_margin)
                price = max(price, price_limit + price_min_margin)

            if self.price_max_margin:
                price_max_margin = convert_to_price_uom(self.price_max_margin)
                price = min(price, price_limit + price_max_margin)
        else:
            price = super()._compute_price(
                price=price, price_uom=price_uom, product=product, quantity=quantity,
                partner=partner)

        return price
