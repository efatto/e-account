# -*- coding: utf-8 -*-

from openerp import fields, models, api, _, exceptions
from email_validator import validate_email, EmailSyntaxError, \
    EmailUndeliverableError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    email_invoice = fields.Char(
        'Invoice Email', help='One single email or a list of email separated by ","')

    @api.multi
    @api.constrains('email_invoice')
    def on_change_email_invoice(self):
        for partner in self:
            if partner.email_invoice:
                if ',' in partner.email_invoice.replace(' ', ''):
                    for mail in partner.email_invoice.replace(' ', '').split(','):
                        if len(mail) > 2:
                            partner.validate_email(mail)
                else:
                    partner.validate_email(partner.email_invoice)

    @staticmethod
    def validate_email(email):
        try:
            validate_email(
                email, check_deliverability=True)
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
