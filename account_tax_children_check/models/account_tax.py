from odoo import _, api, models
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.constrains("children_tax_ids")
    def _check_children_taxes(self):
        for tax in self:
            for child_tax in tax.children_tax_ids:
                if len(child_tax.parent_tax_ids) > 1:
                    raise UserError(
                        _(
                            "Tax %(name)s has already a parent tax: %(parent)s",
                            name=child_tax.name,
                            parent=", ".join(
                                [
                                    "[%s] %s" % (i, name)
                                    for i, name in enumerate(
                                        child_tax.parent_tax_ids.filtered(
                                            lambda x, t=tax: x != t
                                        ).mapped("name"),
                                        1,
                                    )
                                ]
                            ),
                        )
                    )
