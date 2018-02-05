# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, _, models, exceptions


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def generate_email_for_composer_batch(
            self, template_id, res_ids, context=None, fields=None):
        values = super(MailComposeMessage, self
                       ).generate_email_for_composer_batch(
            template_id, res_ids, context=context, fields=fields
        )
        for key in values.keys():
            mail = values[key]
            if 'partner_ids' in mail and mail['partner_ids']:
                for partner in self.env['res.partner'].browse(
                        mail['partner_ids']):
                    if not partner.email:
                        raise exceptions.ValidationError(
                            _('Missing email in partner %s') % partner.name
                        )
        return values
