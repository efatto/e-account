from odoo import api, _, models
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.constrains("children_tax_ids")
    def _check_children_taxes(self):
        for tax in self:
            for child_tax in tax.children_tax_ids:
                if len(child_tax.parent_tax_ids) > 1:
                    raise UserError(_(
                        "Tax %s has already a parent tax: %s") % (
                            child_tax.name,
                            ", ".join(
                                [
                                    "[%s] %s" % (i, name) for i, name in enumerate(
                                        child_tax.parent_tax_ids.filtered(
                                            lambda x: x != tax
                                        ).mapped("name"),
                                        1
                                    )
                                ]
                            )
                        )
                    )
