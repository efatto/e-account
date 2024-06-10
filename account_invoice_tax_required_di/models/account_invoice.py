from odoo import _, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _check_di_line_tax(self):
        di_kind_id = self.env.ref("l10n_it_account_tax_kind.n3_5")
        for invoice in self.filtered(lambda x: x.is_invoice()):
            if any(
                di_kind_id in line.mapped("tax_ids.kind_id")
                and not line.force_declaration_of_intent_id
                and not invoice.declaration_of_intent_ids
                for line in invoice.invoice_line_ids
            ):
                raise UserError(
                    _("Missing declaration of intent for invoice %s") % invoice.name
                )

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        self._check_di_line_tax()
        return res
