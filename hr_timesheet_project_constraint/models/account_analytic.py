from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_project_account_not_the_same = fields.Boolean(
        compute="_compute_is_project_account_not_the_same",
        store=True,
    )
    project_analytic_account_id = fields.Many2one(
        string="Project Analytic Account",
        comodel_name="account.analytic.account",
        related="project_id.analytic_account_id",
    )

    @api.depends("project_id", "account_id")
    def _compute_is_project_account_not_the_same(self):
        for record in self:
            record.is_project_account_not_the_same = (
                record.project_id
                and record.account_id
                and record.account_id != record.project_id.analytic_account_id
            )

    # @api.constrains('project_id', 'account_id')
    # def check_project_account(self):
    #     for record in self:
    #         if (
    #             record.project_id
    #             and record.account_id
    #             and record.account_id
    #             != record.project_id.analytic_account_id
    #         ):
    #             raise ValidationError(_(
    #                 "Analytic account and project analytic account must be the same!"
    #             ))
