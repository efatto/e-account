
from odoo import models, fields


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def export_xls_exploded(self):
        self.ensure_one()
        context = dict(self._context_with_filters())
        return (
            self.env.ref("mis_builder_xlsx_exploded.xls_export_exploded")
            .with_context(context)
            .report_action(self, data=dict(dummy=True))  # required to propagate context
        )


class MisReportKpi(models.Model):
    _inherit = "mis.report.kpi"

    cell_report_expression = fields.Text(
        string="Expression to compute cell name in report",
        help="Field or expression to evaluate to be shown in report xlsx."
             "Possible use of 'record'. E.g.: "
             "'name' or 'product_id.name' or "
             "'" ".join(record.extra_cost_invoice_line_ids.mapped(\"name\"))'"
    )
