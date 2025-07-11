from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = "mrp.workcenter.productivity"

    duration_hour = fields.Float(
        string="Duration (hours)", compute="_compute_duration_hour", store=True
    )

    @api.depends("duration")
    def _compute_duration_hour(self):
        for prod in self:
            prod.duration_hour = prod.duration / 60.0
