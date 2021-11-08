# -*- coding: utf-8 -*-

from openerp import models, api, exceptions, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):
        if self.env.context.get('default_model') == 'account.invoice' and \
                self.env.context.get('default_res_id'):
            if not self.partner_ids:
                raise exceptions.ValidationError(
                    _('Email missing!')
                )
            for partner in self.partner_ids:
                if ',' in partner.email.replace(' ', ''):
                    for mail in partner.email.replace(' ', '').split(','):
                        if len(mail) > 2:
                            partner.validate_email(mail)
                else:
                    partner.validate_email(partner.email)

        return super(MailComposeMessage, self).send_mail()
