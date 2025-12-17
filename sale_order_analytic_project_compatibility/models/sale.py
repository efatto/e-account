from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("analytic_account_id")
    def _onchange_analytic_account_id(self):
        if self.project_id and self.analytic_account_id:
            if self.project_id.analytic_account_id != self.analytic_account_id:
                self.project_id = False
        elif self.analytic_account_id:
            project_ids = self.env["project.project"].search(
                [
                    ("analytic_account_id", "=", self.analytic_account_id.id),
                ]
            )
            if len(project_ids) == 1:
                self.project_id = project_ids[0]

    @api.constrains("project_id", "analytic_account_id")
    def _check_project_analytic_account(self):
        if self.project_id and self.analytic_account_id:
            assert self.project_id.analytic_account_id == self.analytic_account_id
