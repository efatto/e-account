# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, models
from odoo.addons.mis_builder.models.mis_safe_eval import DataError
from odoo.addons.mis_builder.models.mis_report import SubKPIUnknownTypeError, \
    SubKPITupleLengthError
from .kpimatrix import KpiMatrix
from odoo.addons.mis_builder.models.simple_array import named_simple_array

_logger = logging.getLogger(__name__)


class MisReport(models.Model):
    _inherit = "mis.report"

    def prepare_kpi_matrix(self, multi_company=False):
        self.ensure_one()
        kpi_matrix = KpiMatrix(self.env, multi_company, self.account_model)
        for kpi in self.kpi_ids:
            kpi_matrix.declare_kpi(kpi)
        return kpi_matrix

    # override original function - check if possible with super()
    def _declare_and_compute_col(  # noqa: C901 (simplify this fnction)
        self,
        expression_evaluator,
        kpi_matrix,
        col_key,
        col_label,
        col_description,
        subkpis_filter,
        locals_dict,
        no_auto_expand_accounts=False,
    ):
        if subkpis_filter:
            # filter by subkpi names
            subkpis = [subkpi for subkpi in self.subkpi_ids if subkpi in subkpis_filter]
        else:
            subkpis = self.subkpi_ids

        SimpleArray_cls = named_simple_array(
            "SimpleArray_{}".format(col_key), [subkpi.name for subkpi in subkpis]
        )
        locals_dict["SimpleArray"] = SimpleArray_cls

        col = kpi_matrix.declare_col(
            col_key, col_label, col_description, locals_dict, subkpis
        )

        compute_queue = self.kpi_ids
        recompute_queue = []
        while True:
            for kpi in compute_queue:
                # build the list of expressions for this kpi
                expressions = kpi._get_expressions(subkpis)

                (
                    vals,
                    drilldown_args,
                    name_error,
                ) = expression_evaluator.eval_expressions(expressions, locals_dict)
                for drilldown_arg in drilldown_args:
                    if not drilldown_arg:
                        continue
                    drilldown_arg["period_id"] = col_key
                    drilldown_arg["kpi_id"] = kpi.id

                if name_error:
                    recompute_queue.append(kpi)
                else:
                    # no error, set it in locals_dict so it can be used
                    # in computing other kpis
                    if not subkpis or not kpi.multi:
                        locals_dict[kpi.name] = vals[0]
                    else:
                        locals_dict[kpi.name] = SimpleArray_cls(vals)

                # even in case of name error we set the result in the matrix
                # so the name error will be displayed if it cannot be
                # resolved by recomputing later

                if subkpis and not kpi.multi:
                    # here we have one expression for this kpi, but
                    # multiple subkpis (so this kpi is most probably
                    # a sum or other operation on multi-valued kpis)
                    if isinstance(vals[0], tuple):
                        vals = vals[0]
                        if len(vals) != col.colspan:
                            raise SubKPITupleLengthError(
                                _(
                                    'KPI "{}" is valued as a tuple of '
                                    "length {} while a tuple of length {} "
                                    "is expected."
                                ).format(kpi.description, len(vals),
                                         col.colspan)
                            )
                    elif isinstance(vals[0], DataError):
                        vals = (vals[0],) * col.colspan
                    else:
                        raise SubKPIUnknownTypeError(
                            _(
                                'KPI "{}" has type {} while a tuple was '
                                "expected.\n\nThis can be fixed by either:\n\t- "
                                "Changing the KPI value to a tuple of length "
                                "{}\nor\n\t- Changing the "
                                "KPI to `multi` mode and giving an explicit "
                                "value for each sub-KPI."
                            ).format(kpi.description, type(vals[0]),
                                     col.colspan)
                        )
                if len(drilldown_args) != col.colspan:
                    drilldown_args = [None] * col.colspan

                kpi_matrix.set_values(kpi, col_key, vals, drilldown_args)

                # ADD for partner stuff
                if kpi.auto_expand_partners:
                    for (
                        partner_id,
                        vals,
                        drilldown_args,
                        _name_error,
                    ) in expression_evaluator.eval_expressions_by_partner(
                        expressions, locals_dict, self
                    ):
                        for drilldown_arg in drilldown_args:
                            if not drilldown_arg:
                                continue
                            drilldown_arg["period_id"] = col_key
                            drilldown_arg["kpi_id"] = kpi.id
                        kpi_matrix.set_values_detail_partner(
                            kpi, col_key, partner_id, vals, drilldown_args
                        )
                # END ADD

                if (
                    name_error
                    or no_auto_expand_accounts
                    or not kpi.auto_expand_accounts
                ):
                    continue

                for (
                    account_id,
                    vals,
                    drilldown_args,
                    _name_error,
                ) in expression_evaluator.eval_expressions_by_account(
                    expressions, locals_dict
                ):
                    for drilldown_arg in drilldown_args:
                        if not drilldown_arg:
                            continue
                        drilldown_arg["period_id"] = col_key
                        drilldown_arg["kpi_id"] = kpi.id
                    kpi_matrix.set_values_detail_account(
                        kpi, col_key, account_id, vals, drilldown_args
                    )

            if len(recompute_queue) == 0:
                # nothing to recompute, we are done
                break
            if len(recompute_queue) == len(compute_queue):
                # could not compute anything in this iteration
                # (ie real Name errors or cyclic dependency)
                # so we stop trying
                break
                # try again
            compute_queue = recompute_queue
            recompute_queue = []
