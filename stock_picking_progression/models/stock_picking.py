from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    progress = fields.Float(
        compute="_compute_qty", store=True, string=" ", group_operator=None)
    progress_text = fields.Char(
        string="Progress",
        store=True,
        compute="_compute_qty",
    )
    total_qty = fields.Float(compute="_compute_qty", store=True, group_operator="sum")
    done_qty = fields.Float(compute="_compute_qty", store=True, group_operator="sum")

    @api.depends("move_lines", "move_lines.quantity_done", "move_lines.product_uom_qty")
    def _compute_qty(self):
        for record in self:
            total_qty = sum(record.mapped("move_lines.product_uom_qty"))
            record.total_qty = total_qty
            done_qty = sum(record.mapped("move_lines.quantity_done"))
            record.done_qty = done_qty
            record.progress = (
                100
                if (record.state == "done" or not total_qty)
                else (
                    sum(
                        min(x.quantity_done, x.product_uom_qty)
                        for x in record.move_lines
                    )
                    / total_qty
                    * 100
                )
            )
            record.progress_text = "%s/%s" % (
                done_qty,
                total_qty,
            )
