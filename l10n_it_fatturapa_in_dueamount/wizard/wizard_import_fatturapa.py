# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class WizardImportFatturapa(models.TransientModel):
    _inherit = "wizard.import.fatturapa"

    def set_payments_data(self, FatturaBody, invoice_id, partner_id):
        super().set_payments_data(FatturaBody, invoice_id, partner_id)
        PaymentsData = FatturaBody.DatiPagamento
        if PaymentsData:
            # set due lines to create correct payment in account move
            invoice = self.env['account.invoice'].browse(invoice_id)
            dueamount_line_obj = self.env['account.invoice.dueamount.line']
            due_line_ids = []
            for PaymentLine in PaymentsData:
                details = PaymentLine.DettaglioPagamento or False
                if details:
                    for dline in details:
                        due_line_id = dueamount_line_obj.create({
                            'date': dline.DataScadenzaPagamento or False,
                            'amount': dline.ImportoPagamento or 0.0,
                            'invoice_id': invoice.id,
                        })
                        due_line_ids.append(due_line_id.id)
                if due_line_ids:
                    invoice.write({
                        'dueamount_line_ids': [(6, 0, due_line_ids)]})
