from odoo import api, fields, models,  _
from odoo.exceptions import UserError


class MisReportKpi(models.Model):
    _inherit = "mis.report.kpi"

    auto_expand_partners = fields.Boolean(string="Display details by partner")

    @api.multi
    @api.constrains("auto_expand_partners", "query_id")
    def check_auto_expand_partners(self):
        for mis_report_kpi in self:
            if mis_report_kpi.auto_expand_partners and not mis_report_kpi.query_id:
                raise UserError(_("Linked query is required when auto expand partners "
                                  "is enabled!"))
            if mis_report_kpi.auto_expand_partners \
                    and not mis_report_kpi.query_id.field_partner_id:
                raise UserError(_("Partner field is required when auto expand "
                                  "partners is enabled!"))
