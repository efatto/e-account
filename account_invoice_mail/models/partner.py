# -*- coding: utf-8 -*-

from openerp import fields, models, api, _, exceptions
from email_validator import validate_email, EmailSyntaxError, \
    EmailUndeliverableError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    email_invoice = fields.Char('Invoice Email')

    @api.multi
    @api.constrains('email_invoice')
    def on_change_email_invoice(self):
        for partner in self:
            if partner.email_invoice:
                try:
                    validate_email(
                        partner.email_invoice, check_deliverability=True)
                except EmailSyntaxError as error:
                    raise exceptions.ValidationError(
                        _("That does not seem to be an email address. \n %s"
                          % str(error)),
                    )
                except EmailUndeliverableError as error:
                    raise exceptions.ValidationError(
                        _("That does not seem to be a deliverable email"
                          " address. \n %s"
                          % str(error)),
                    )
                except Exception as error:
                    raise exceptions.ValidationError(
                        _("An error occurred validating email address. \n %s"
                          % str(error)),
                    )
