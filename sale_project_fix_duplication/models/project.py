from odoo import _, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def create(self, vals):
        # Always assign type_ids to project to avoid creation of New type at every
        # _timesheet_create_project (see PR https://github.com/OCA/OCB/pull/1186)
        res = super(ProjectProject, self).create(vals)
        if not res.type_ids:
            type_ids = self.env["project.task.type"].search(
                [("name", "=", _("New"))], limit=1
            )
            if not type_ids:
                type_ids = self.env["project.task.type"].create({"name": _("New")})
            res.type_ids = type_ids
        return res
