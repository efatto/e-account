# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_intrastat_data(self):
        """
        Get the intrastat code with this priority when it is an out invoice/refund:
        - Intrastat Code on product category
        - Intrastat Code on product template
        """
        res = super().get_intrastat_data()
        if self._context.get("move_type", "") in ["out_invoice", "out_refund"]:
            if self.categ_id and self.categ_id.intrastat_code_id:
                res["intrastat_code_id"] = self.categ_id.intrastat_code_id.id
                res["intrastat_type"] = self.categ_id.intrastat_type
        return res
