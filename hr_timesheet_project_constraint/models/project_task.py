from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    original_sale_line_id = fields.Many2one(
        "sale.order.line", "Original Sale Order Line"
    )

    @api.depends(
        "original_sale_line_id",
        "sale_line_id",
        "project_id",
        "allow_billable",
        "non_allow_billable",
    )
    def _compute_sale_order_id(self):
        res = super()._compute_sale_order_id()
        for task in self.filtered("original_sale_line_id"):
            if (
                task.allow_billable
                and task.bill_type == "customer_task"
                and (
                    task.original_sale_line_id.order_id.analytic_account_id
                    or task.original_sale_line_id.order_id.project_id.analytic_account_id
                )
            ):
                task.sale_order_id = task.original_sale_line_id.sudo().order_id
        return res
