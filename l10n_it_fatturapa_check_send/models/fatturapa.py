# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SendPEC(models.TransientModel):
    _inherit = 'wizard.fatturapa.send.pec'

    @api.multi
    def send_pec(self):
        if self.env.context.get('active_ids'):
            attachments = self.env['fatturapa.attachment.out'].browse(
                self.env.context['active_ids'])
            for inv in attachments.mapped('out_invoice_ids'):
                if inv.partner_id.codice_destinatario == 'XXXXXXX'\
                        and inv.period_id.disable_send_foreign_invoice:
                    raise UserError(
                        _("You can only send files for Italian partners for %s period."
                          % inv.period_id.code)
                    )
        return super(SendPEC, self).send_pec()


class FatturaPAAttachmentOut(models.Model):
    _inherit = 'fatturapa.attachment.out'

    @api.multi
    def send_via_pec(self):
        for inv in self.out_invoice_ids:
            if inv.partner_id.codice_destinatario == 'XXXXXXX' \
                    and inv.period_id.disable_send_foreign_invoice:
                raise UserError(
                    _("You can only send files for Italian partners for %s period."
                      % inv.period_id.code)
                )
        return super(FatturaPAAttachmentOut, self).send_via_pec()
