from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_standard_price = fields.Float(
        string="Product Cost", related="product_id.standard_price"
    )
    move_price_unit = fields.Float(
        string="Move Cost Unit",
        compute="_compute_move_price_unit",
        compute_sudo=True,
        inverse="_inverse_move_price_unit",
        store=True,
    )
    move_price_delivering_total = fields.Float(
        string="Total Delivering Costs",
        compute_sudo=True,
        compute="_compute_move_price_unit",
        store=False
    )
    move_price_invoiced_total = fields.Float(
        string="Total Invoiced Costs",
        compute_sudo=True,
        compute="_compute_move_price_unit",
        store=False
    )
    move_price_to_invoice_total = fields.Float(
        string="Total Cost To Invoice",
        compute="_compute_move_price_unit",
        compute_sudo=True,
        store=False,
        help="This cost is only computed when products can be sold but not purchased.",
    )

    @api.depends("move_ids.price_unit")
    def _compute_move_price_unit(self):
        for line in self:
            # preserve negative values as costs
            line.move_price_unit = min(
                [-abs(x.price_unit) for x in line.move_ids] or [0]
            )
            price = (
                line.move_price_unit
                if line.move_price_unit != 0.0
                else -line.product_standard_price
            )
            qty_max_delivery = max([line.qty_delivered, line.product_qty])
            line.move_price_delivering_total = price * qty_max_delivery
            line.move_price_invoiced_total = price * line.qty_invoiced
            if line.product_id.purchase_ok:
                # this product can be purchased so if we consider it could lead to a
                # duplication of costs
                line.move_price_to_invoice_total = 0
            else:
                line.move_price_to_invoice_total = price * (
                    qty_max_delivery - line.qty_invoiced
                )

    def _inverse_move_price_unit(self):
        self.ensure_one()
        if self.move_ids and self.move_price_unit:
            for move in self.move_ids:
                move.price_unit = self.move_price_unit
