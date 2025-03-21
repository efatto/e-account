
from odoo import models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def drilldown(self, arg):
        res = super().drilldown(arg=arg)
        if arg.get("model", False) == "sale.order.progress":
            res.update({
                "views": [
                    [
                        self.env.ref(
                            'mis_builder_query_drilldown_view_sop.view_order_progress_tree'
                        ).id, 'list'
                    ], [False, 'form']
                ],
            })
        return res
