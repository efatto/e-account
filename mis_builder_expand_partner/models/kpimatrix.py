# Copyright 2014 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.mis_builder.models.mis_safe_eval import DataError, mis_safe_eval
from odoo.addons.mis_builder.models.kpimatrix import KpiMatrix, KpiMatrixRow, \
    KpiMatrixCell

try:
    import itertools.izip as zip
except ImportError:
    pass  # python 3


_logger = logging.getLogger(__name__)


class KpiMatrixRow(KpiMatrixRow):

    def __init__(self, matrix, kpi, account_id=None, parent_row=None, partner_id=None):
        super().__init__(matrix=matrix, kpi=kpi, account_id=account_id,
                         parent_row=parent_row)
        self.partner_id = partner_id

    @property
    def label(self):
        if self.partner_id:
            return self._matrix._partner_model.browse(self.partner_id).name
        if not self.account_id:
            return self.kpi.description
        else:
            return self._matrix.get_account_name(self.account_id)


class KpiMatrix(KpiMatrix):

    def __init__(self, env, multi_company=False, account_model="account.account"):
        super().__init__(env=env, multi_company=multi_company,
                         account_model=account_model)
        self._partner_model = env["res.partner"]

    def set_values_detail_partner(
        self, kpi, col_key, partner_id, vals, drilldown_args, tooltips=True
    ):
        """Set values for a kpi and a column and a detail account.
        Invoke this after declaring the kpi and the column.
        """
        if not partner_id:
            row = self._kpi_rows[kpi]
        else:
            kpi_row = self._kpi_rows[kpi]
            if partner_id in self._detail_rows[kpi]:
                row = self._detail_rows[kpi][partner_id]
            else:
                row = KpiMatrixRow(self, kpi, partner_id=partner_id, parent_row=kpi_row)
                self._detail_rows[kpi][partner_id] = row
        col = self._cols[col_key]
        cell_tuple = []
        assert len(vals) == col.colspan
        assert len(drilldown_args) == col.colspan
        for val, drilldown_arg, subcol in zip(vals, drilldown_args, col.iter_subcols()):
            if isinstance(val, DataError):
                val_rendered = val.name
                val_comment = val.msg
            else:
                val_rendered = self._style_model.render(
                    self.lang, row.style_props, kpi.type, val
                )
                if row.kpi.multi and subcol.subkpi:
                    val_comment = u"{}.{} = {}".format(
                        row.kpi.name,
                        subcol.subkpi.name,
                        row.kpi._get_expression_str_for_subkpi(subcol.subkpi),
                    )
                else:
                    val_comment = u"{} = {}".format(row.kpi.name, row.kpi.expression)
            cell_style_props = row.style_props
            if row.kpi.style_expression:
                # evaluate style expression
                try:
                    style_name = mis_safe_eval(
                        row.kpi.style_expression, col.locals_dict
                    )
                except Exception:
                    _logger.error(
                        "Error evaluating style expression <%s>",
                        row.kpi.style_expression,
                        exc_info=True,
                    )
                if style_name:
                    style = self._style_model.search([("name", "=", style_name)])
                    if style:
                        cell_style_props = self._style_model.merge(
                            [row.style_props, style[0]]
                        )
                    else:
                        _logger.error("Style '%s' not found.", style_name)
            cell = KpiMatrixCell(
                row,
                subcol,
                val,
                val_rendered,
                tooltips and val_comment or None,
                cell_style_props,
                drilldown_arg,
                kpi.type,
            )
            cell_tuple.append(cell)
        assert len(cell_tuple) == col.colspan
        col._set_cell_tuple(row, cell_tuple)
