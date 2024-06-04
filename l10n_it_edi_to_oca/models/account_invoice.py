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
