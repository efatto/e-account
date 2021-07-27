# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def drilldown(self, arg):
        res = super().drilldown(arg=arg)
        if arg.get("model", False) == "account.invoice.line":
            res.update({
                "views": [[self.env.ref(
                    'mis_builder_query_drilldown_view.view_invoice_line_tree').id,
                    'list'], [False, 'form']],
            })
        if arg.get("model", False) == "sale.order.line":
            res.update({
                "views": [[self.env.ref(
                    'mis_builder_query_drilldown_view.view_order_line_tree').id,
                           'list'], [False, 'form']],
            })
        if arg.get("model", False) == "account.analytic.line":
            res.update({
                "views": [[self.env.ref(
                    'mis_builder_query_drilldown_view.view_account_analytic_line_tree'
                ).id, 'list'], [False, 'form']],
            })
        return res
