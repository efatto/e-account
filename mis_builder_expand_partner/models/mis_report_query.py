from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MisReportQuery(models.Model):
    _inherit = "mis.report.query"

    field_partner_id = fields.Many2one(
        "ir.model.fields", string="Partner field to expand by",
    )

    @api.multi
    @api.constrains("field_ids", "field_partner_id")
    def check_field_partner_id(self):
        for mis_report_query in self:
            if mis_report_query.field_partner_id and \
                    len(mis_report_query.field_ids) != 1:
                raise UserError(_("Query with partner expansion can have "
                                  "only 1 field selected!"))
