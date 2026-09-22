# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Carlos Roca
# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    delivery_method_id = fields.Many2one(
        comodel_name="delivery.carrier",
        string="Delivery Method",
        check_company=True,
    )
    is_all_service = fields.Boolean(
        "Service Product", compute="_compute_is_service_products"
    )

    @api.depends(
        "invoice_line_ids.product_id.type",
        "invoice_line_ids.is_delivery",
    )
    def _compute_is_service_products(self):
        for invoice in self:
            invoice.is_all_service = all(
                line.product_id.type == "service"
                for line in invoice.invoice_line_ids.filtered(
                    lambda line: line.product_id and not line.is_delivery
                )
            )

    def _is_auto_add_delivery_line(self):
        self.ensure_one()
        return self.company_id.sale_auto_add_delivery_line

    def _auto_refresh_delivery(self):
        self.ensure_one()
        if (
            self.env.context.get("auto_refresh_delivery")
            or not self._is_auto_add_delivery_line()
            or self.state != "draft"
            or not self.is_sale_document(include_receipts=True)
        ):
            return
        self = self.with_company(self.company_id).with_context(
            auto_refresh_delivery=True
        )
        if not self.delivery_method_id or self.is_all_service:
            self._remove_delivery_line()
        else:
            price_unit = self.rate_shipment(self.delivery_method_id)["price"]
            delivery_lines = self.invoice_line_ids.filtered("is_delivery")
            if not delivery_lines:
                self._create_delivery_line(self.delivery_method_id, price_unit)
            else:
                delivery_line = delivery_lines[:1]
                if len(delivery_lines) > 1:
                    # Grouped invoices must retain all originating sales lines.
                    delivery_line.write(
                        {
                            "sale_line_ids": [
                                Command.set(delivery_lines.sale_line_ids.ids)
                            ],
                            "discount": delivery_lines[-1:].discount,
                        }
                    )
                    (delivery_lines - delivery_line).unlink()
                self._update_delivery_line(delivery_line, price_unit)

    @api.model_create_multi
    def create(self, vals_list):
        """Create or refresh delivery line on create of customer invoices/refund."""
        # Suppress refreshes from nested writes while Odoo creates the invoice.
        invoices = super(
            AccountMove, self.with_context(auto_refresh_delivery=True)
        ).create(vals_list)
        invoices = invoices.with_env(self.env)
        for invoice in invoices:
            invoice._auto_refresh_delivery()
        return invoices

    def write(self, vals):
        """Create or refresh the delivery line after saving."""
        res = super(AccountMove, self.with_context(auto_refresh_delivery=True)).write(
            vals
        )
        for invoice in self:
            invoice._auto_refresh_delivery()
        return res

    def _update_order_line_info(self, product_id, quantity, **kwargs):
        # The catalog changes invoice lines directly, without writing the move.
        res = super()._update_order_line_info(product_id, quantity, **kwargs)
        self._auto_refresh_delivery()
        return res

    def button_update_prices_from_pricelist(self):
        res = super().button_update_prices_from_pricelist()
        for invoice in self:
            invoice._auto_refresh_delivery()
        return res

    def _compute_amount_total_without_delivery(self):
        self.ensure_one()
        use_price_untaxed = self.delivery_method_id.use_price_untaxed
        delivery_cost = sum(
            self.invoice_line_ids.filtered("is_delivery").mapped(
                "price_subtotal" if use_price_untaxed else "price_total"
            )
        )
        return (
            self.amount_untaxed if use_price_untaxed else self.amount_total
        ) - delivery_cost

    def rate_shipment(self, carrier):
        """
        Compute invoice shipping using the same pricing steps as delivery.carrier.
        :param carrier: record of delivery.carrier
        :return dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
        """
        self.ensure_one()
        carrier.ensure_one()
        if hasattr(carrier, f"{carrier.delivery_type}_rate_shipment"):
            res = getattr(carrier, f"{carrier.delivery_type}_rate_shipment")(self)
            # apply fiscal position
            company = carrier.company_id or self.company_id or self.env.company
            # use untaxed price in use_price_untaxed it true, setting a void recordset
            res["price"] = carrier.product_id._get_tax_included_unit_price(
                company,
                self.currency_id,
                self.invoice_date or fields.Date.context_today(self),
                "sale",
                fiscal_position=self.fiscal_position_id,
                product_price_unit=res["price"],
                product_taxes=self.env["account.tax"]
                if carrier.use_price_untaxed
                else None,
                product_currency=self.currency_id,
            )
            # apply margin on computed price
            res["price"] = carrier.with_context(order=self)._apply_margins(res["price"])
            # save the real price in case a free_over rule overide it to 0
            res["carrier_price"] = res["price"]
            # free when order is large enough
            if (
                res["success"]
                and carrier.free_over
                and carrier.delivery_type != "base_on_rule"
                and carrier._compute_currency(
                    self,
                    self._compute_amount_total_without_delivery(),
                    "pricelist_to_company",
                )
                >= carrier.amount
            ):
                res["warning_message"] = _(
                    "The shipping is free since the order amount exceeds %(amount).2f.",
                    amount=carrier.amount,
                )
                res["price"] = 0.0
            return res
        else:
            return {
                "success": False,
                "price": 0.0,
                "error_message": _("Error: this delivery method is not available."),
                "warning_message": False,
            }

    def _prepare_delivery_line_vals(self, carrier, price_unit):
        self.ensure_one()
        if self.partner_id:
            carrier = carrier.with_context(lang=self.partner_id.lang)

        # Apply fiscal position
        taxes = carrier.product_id.taxes_id._filter_taxes_by_company(self.company_id)
        taxes_ids = taxes.ids
        if self.partner_id and self.fiscal_position_id:
            taxes_ids = self.fiscal_position_id.map_tax(taxes).ids

        # Create the account move line
        if carrier.product_id.description_sale:
            so_description = f"{carrier.name}: {carrier.product_id.description_sale}"
        else:
            so_description = carrier.name
        values = {
            "move_id": self.id,
            "partner_id": self.partner_id.id,
            "name": so_description,
            "sequence": 99999,
            "quantity": 1,
            "product_uom_id": carrier.product_id.uom_id.id,
            "product_id": carrier.product_id.id,
            "tax_ids": [Command.set(taxes_ids)],
            "is_delivery": True,
            "price_unit": price_unit,
        }
        accounts = carrier.product_id.with_company(
            self.company_id
        ).product_tmpl_id.get_product_accounts(fiscal_pos=self.fiscal_position_id)
        values["account_id"] = (
            accounts["income"] or self.journal_id.default_account_id
        ).id
        if carrier.free_over and self.currency_id.is_zero(price_unit):
            values["name"] += "\n" + _("Free Shipping")
        return values

    def _create_delivery_line(self, carrier, price_unit):
        if not self._origin:
            return self.env["account.move.line"]
        values = self._prepare_delivery_line_vals(carrier, price_unit)
        return self.env["account.move.line"].create(values)

    def _update_delivery_line(self, delivery_line, price_unit):
        """Refresh changed values without losing discounts or sales line links."""
        values = self._prepare_delivery_line_vals(self.delivery_method_id, price_unit)
        new_vals = {}
        for name, value in values.items():
            field = delivery_line._fields[name]
            if name == "sequence":
                continue
            if isinstance(field, fields.One2many | fields.Many2many):
                if any(command[0] != Command.SET for command in value):
                    new_vals[name] = [Command.clear()] + value
                elif any(
                    set(delivery_line[name].ids) != set(command[2]) for command in value
                ):
                    new_vals[name] = value
            elif isinstance(field, fields.Many2one):
                if delivery_line[name].id != value:
                    new_vals[name] = value
            elif delivery_line[name] != value:
                new_vals[name] = value
        if new_vals:
            delivery_line.write(new_vals)

    def _remove_delivery_line(self):
        self.invoice_line_ids.filtered("is_delivery").unlink()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_delivery = fields.Boolean(string="Is a Delivery", default=False)

    @api.depends("quantity")
    def _compute_price_unit(self):
        # Delivery charges come from the carrier, not the invoice pricelist.
        return super(
            AccountMoveLine, self.filtered(lambda line: not line.is_delivery)
        )._compute_price_unit()
