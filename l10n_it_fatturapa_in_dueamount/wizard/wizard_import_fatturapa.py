# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import float_compare

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
                    # if total payment details is not equal to amount total, ignore
                    if not float_compare(
                        invoice.amount_total,
                        float(sum(x.ImportoPagamento for x in details)),
                        precision_digits=2
                    ):
                        for dline in details:
                            if dline.DataScadenzaPagamento and dline.ImportoPagamento:
                                due_line_id = dueamount_line_obj.create([{
                                    'date': dline.DataScadenzaPagamento,
                                    'amount': dline.ImportoPagamento,
                                    'invoice_id': invoice.id,
                                }])
                                due_line_ids.append(due_line_id.id)
                if due_line_ids:
                    invoice.write({
                        'dueamount_line_ids': [(6, 0, due_line_ids)]})
