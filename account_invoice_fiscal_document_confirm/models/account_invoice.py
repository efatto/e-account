from odoo import _, api, models, fields
from odoo.fields import first


class AccountInvoice(models.Model):
    _inherit = "account.move"

    is_fiscal_document_type_default = fields.Boolean(
        compute="_compute_is_fiscal_document_type_not_default",
        store=True,
    )

    @api.depends("fiscal_document_type_id", "move_type")
    def _compute_is_fiscal_document_type_not_default(self):
        default_fiscal_document_type_id = first(
            self.env["fiscal.document.type"].search(
                [("out_invoice", "=", True)]
            )
        )
        for invoice in self:
            self.is_fiscal_document_type_default = (
                invoice.move_type == "out_invoice"
                and invoice.fiscal_document_type_id
                == default_fiscal_document_type_id
            )
