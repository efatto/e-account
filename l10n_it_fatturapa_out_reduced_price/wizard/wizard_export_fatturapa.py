
from odoo import models


class WizardExportFatturapa(models.TransientModel):
    _inherit = "wizard.export.fatturapa"

    def setScontoMaggiorazione(self, line):
        if (
            line.invoice_id.partner_id.export_invoice_reduced_price
            or self.env.user.company_id.export_invoice_reduced_price
        ) and line.is_exportable_reduced_price:
            return []
        return super().setScontoMaggiorazione(line)

    def _get_prezzo_unitario(self, line):
        if (
            line.invoice_id.partner_id.export_invoice_reduced_price
            or self.env.user.company_id.export_invoice_reduced_price
        ) and line.is_exportable_reduced_price:
            return line.price_reduced_tax_excluded
        return super()._get_prezzo_unitario(line)
