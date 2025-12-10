from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = "account.move"

    auto_recompute_intrastat = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(
            AccountInvoice,
            self.with_context(no_recurse_compute_intrastat=True)
        ).create(vals_list)
        if res.intrastat and res.auto_recompute_intrastat:
            res.compute_intrastat_lines()
        return res

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("no_recurse_compute_intrastat"):
            for inv in self:
                if inv.intrastat and inv.auto_recompute_intrastat:
                    inv.with_context(
                        no_recurse_compute_intrastat=True
                    ).compute_intrastat_lines()
        return res
