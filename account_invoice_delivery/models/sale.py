from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoice_grouping_keys(self):
        return super()._get_invoice_grouping_keys() + ["delivery_method_id"]

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update(delivery_method_id=self.carrier_id.id)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update(is_delivery=self.is_delivery)
        return res
