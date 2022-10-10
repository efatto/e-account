# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FatturaPAAttachmentOut(models.Model):
    _inherit = "fatturapa.attachment.out"

    is_pa = fields.Boolean(
        related='invoice_partner_id.is_pa',
        store=True,
    )
    is_pa_sendable = fields.Boolean(
        compute='_compute_is_pa_sendable',
        store=True,
    )

    @api.multi
    @api.depends('is_pa', 'datas_fname')
    def _compute_is_pa_sendable(self):
        for att in self:
            att.is_pa_sendable = bool(
                self.env.user.company_id.sdi_channel_id.is_pa_sign_automatic or
                not att.is_pa or
                (att.is_pa and att.datas_fname.split('.')[-1] == 'p7m')
            )
