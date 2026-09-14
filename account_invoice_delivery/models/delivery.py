# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def _get_price_available(self, order):
        self.ensure_one()
        if order._name != "account.move":
            return super()._get_price_available(order)
        self = self.sudo()
        invoice = order.sudo()
        weight = volume = quantity = wv = 0.0
        for line in invoice.invoice_line_ids:
            if (
                not line.product_id
                or line.is_delivery
                or line.product_id.type in {"service", "combo"}
            ):
                continue
            qty = line.product_uom_id._compute_quantity(
                line.quantity, line.product_id.uom_id
            )
            weight += line.product_id.weight * qty
            volume += line.product_id.volume * qty
            wv += line.product_id.weight * line.product_id.volume * qty
            quantity += qty
        total = self._compute_currency(
            invoice,
            invoice._compute_amount_total_without_delivery(),
            "pricelist_to_company",
        )
        weight = self.env.context.get("order_weight") or weight
        return self._get_price_from_picking(total, weight, volume, quantity, wv=wv)

    def _get_conversion_currencies(self, order, conversion):
        if order._name != "account.move":
            return super()._get_conversion_currencies(order, conversion)
        company_currency = (self.company_id or order.company_id).currency_id
        if conversion == "company_to_pricelist":
            return company_currency, order.currency_id
        return order.currency_id, company_currency

    def _compute_currency(self, order, price, conversion):
        if order._name != "account.move":
            return super()._compute_currency(order, price, conversion)
        from_currency, to_currency = self._get_conversion_currencies(order, conversion)
        if from_currency == to_currency:
            return price
        return from_currency._convert(
            price,
            to_currency,
            order.company_id,
            order.invoice_date or fields.Date.context_today(order),
        )

    def fixed_rate_shipment(self, order):
        if order._name != "account.move":
            return super().fixed_rate_shipment(order)
        self.ensure_one()
        if not self._match_address(order.partner_shipping_id):
            return {
                "success": False,
                "price": 0.0,
                "error_message": _(
                    "Error: this delivery method is not available for this address."
                ),
                "warning_message": False,
            }
        if order.pricelist_id:
            price = order.pricelist_id._get_product_price(
                self.product_id,
                1.0,
                currency=order.currency_id,
                date=order.invoice_date or fields.Date.context_today(order),
            )
        else:
            price = self._compute_currency(
                order, self.fixed_price, "company_to_pricelist"
            )
        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": False,
        }
