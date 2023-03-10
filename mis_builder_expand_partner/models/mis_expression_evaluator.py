import pytz
from collections import defaultdict

from odoo import fields
from odoo.tools import safe_eval
from odoo.tools.date_utils import relativedelta
from odoo.addons.mis_builder.models.mis_safe_eval import mis_safe_eval
from odoo.addons.mis_builder.models.expression_evaluator import ExpressionEvaluator


class MisExpressionEvaluator(ExpressionEvaluator):

    def __init__(
        self,
        aep,
        date_from,
        date_to,
        target_move=None,
        additional_move_line_filter=None,
        aml_model=None,
        companies=None
    ):
        super().__init__(
            aep=aep, date_from=date_from, date_to=date_to, target_move=target_move,
            additional_move_line_filter=additional_move_line_filter,
            aml_model=aml_model)
        self.companies = companies

    def replace_exprs_by_partner_id(self, exprs, locals_dict, mis_report):
        partner_ids = set()
        # _data = defaultdict(dict)
        partner_ids_data = defaultdict(dict)
        for expr in exprs:
            mis_report_queries = list(filter(
                lambda x: isinstance(x, mis_report.env['mis.report.query'].__class__),
                list(locals_dict)))
            query_name = expr.split('.')[0]
            if not query_name:
                continue
            mis_report_queries = [x for x in mis_report_queries if x.name == query_name]
            for mis_report_query in mis_report_queries:
                mis_report_kpi = mis_report_query.report_id.kpi_ids.filtered(
                    lambda x: x.name == mis_report_query.name
                )
                if mis_report_kpi:
                    partner_field_name = mis_report_query.field_partner_id.name
                    mis_fields = mis_report_query.mapped('field_ids.name')
                    date_from = locals_dict['date_from']
                    dt_from = fields.Datetime.from_string(date_from)
                    local_tz = pytz.timezone(mis_report.env.user.tz)
                    date_tz_from = local_tz.localize(dt_from).astimezone(pytz.utc)
                    date_to = locals_dict['date_to']
                    date_to_next_day = date_to + relativedelta(days=1)
                    dt_to = fields.Datetime.from_string(date_to_next_day)
                    date_tz_to = local_tz.localize(dt_to).astimezone(pytz.utc)
                    # Set date_to to next day as date could be a datetime, and filter
                    # using <
                    # Need to localize dates, as they are date() and in database are
                    # stored as UTC
                    # e.g.: 01/09/21 00:00:00 is stored as 31/08/21 22:00:00 in database
                    # so removed offset
                    query_domain = safe_eval(mis_report_query.domain)
                    query_domain.append(
                        ('%s.company_id' % partner_field_name, 'in', self.companies.ids)
                    )
                    query_domain.append(
                        (mis_report_query.date_field.name, '>=', date_tz_from))
                    query_domain.append(
                        (mis_report_query.date_field.name, '<', date_tz_to))
                    result = mis_report.env[mis_report_query.model_id.model].read_group(
                        query_domain, mis_fields, partner_field_name)
                    for res in result:
                        partner_id = res[partner_field_name][0]
                        partner_ids_data.update({
                            partner_id: "(" + repr(res[mis_fields[0]]) + ")"
                        })
                        partner_ids.add(partner_id)

        for partner_id in partner_ids:
            yield partner_id, [partner_ids_data[partner_id]]

    def eval_expressions_by_partner(self, expressions, locals_dict, mis_report):
        if not self:
            return
        exprs = [e and e.name or "AccountingNone" for e in expressions]
        for partner_id, replaced_exprs in self.replace_exprs_by_partner_id(
                exprs, locals_dict, mis_report):
            vals = []
            drilldown_args = []
            name_error = False
            for expr, replaced_expr in zip(exprs, replaced_exprs):
                val = mis_safe_eval(replaced_expr, locals_dict)
                vals.append(val)
                if replaced_expr != expr:
                    drilldown_args.append({"expr": expr, "partner_id": partner_id})
                else:
                    drilldown_args.append(None)
            yield partner_id, vals, drilldown_args, name_error
