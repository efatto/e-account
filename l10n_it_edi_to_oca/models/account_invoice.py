from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    fatturapa_state = fields.Selection(
        [
            ("ready", "Ready to Send"),
            ("sent", "Sent"),
            ("delivered", "Delivered"),
            ("accepted", "Accepted"),
            ("error", "Error"),
        ]
    )
    tax_stamp = fields.Boolean(
        "Tax Stamp",
    )
    # fatturapa_attachment_out_id = fields.Many2one(
    #     "fatturapa.attachment.out",
    # )
    # se installato l10n_it_edi_sdicoop
    # l10n_it_edi_transaction = fields.Char(
    #     copy=False, string="FatturaPA Transaction")
    # l10n_it_edi_attachment_id = fields.Many2one(
    #     'ir.attachment', copy=False, string="FatturaPA Attachment",
    #     ondelete="restrict")
