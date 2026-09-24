from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    progress = fields.Float(
        compute="_compute_qty", store=True, string=" ", aggregator=None
    )
    progress_text = fields.Char(
        string="Progress",
        store=True,
        compute="_compute_qty",
    )
    total_qty = fields.Float(compute="_compute_qty", store=True, aggregator="sum")
    done_qty = fields.Float(compute="_compute_qty", store=True, aggregator="sum")

    @api.depends("move_ids", "move_ids.quantity", "move_ids.product_uom_qty")
    def _compute_qty(self):
        for record in self:
            total_qty = sum(record.mapped("move_ids.product_uom_qty"))
            record.total_qty = total_qty
            done_qty = sum(record.mapped("move_ids.quantity"))
            record.done_qty = done_qty
            record.progress = (
                100
                if (record.state == "done" or not total_qty)
                else (
                    sum(min(x.quantity, x.product_qty) for x in record.move_ids)
                    / total_qty
                    * 100
                )
            )
            record.progress_text = f"{done_qty}/{total_qty}"
