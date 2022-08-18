from odoo import models,  _
from odoo.exceptions import UserError
from .mis_expression_evaluator import MisExpressionEvaluator


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def _add_column_move_lines(self, aep, kpi_matrix, period, label, description):
        if not period.date_from or not period.date_to:
            raise UserError(
                _("Column %s with move lines source must have from/to dates.")
                % (period.name,)
            )
        # Use custom MisExpressionEvaluator to inject partner stuff
        expression_evaluator = MisExpressionEvaluator(
            aep,
            period.date_from,
            period.date_to,
            None,  # target_move now part of additional_move_line_filter
            period._get_additional_move_line_filter(),
            period._get_aml_model_name(),
            companies=self.company_ids | self.company_id,
        )
        self.report_id._declare_and_compute_period(
            expression_evaluator,
            kpi_matrix,
            period.id,
            label,
            description,
            period.subkpi_ids,
            period._get_additional_query_filter,
            no_auto_expand_accounts=self.no_auto_expand_accounts,
        )
