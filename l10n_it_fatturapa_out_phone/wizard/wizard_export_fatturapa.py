# -*- coding: utf-8 -*-
# Copyright 2014 Davide Corio
# Copyright 2015-2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Gianmarco Conte, Marco Calcagni - Dinamiche Aziendali srl
# Copyright 2018 Sergio Corato
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import phonenumbers

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError

from openerp.addons.l10n_it_fatturapa.bindings.fatturapa_v_1_2 import (
    ContattiTrasmittenteType,
    ContattiType,
)


class WizardExportFatturapa(models.TransientModel):
    _inherit = "wizard.export.fatturapa"

    def _setContattiTrasmittente(self, company, fatturapa):

        if not company.phone:
            raise UserError(
                _('Company Telephone number not set.'))
        Telefono = self.checkSetupPhone(company.phone)

        if not company.email:
            raise UserError(
                _('Email address not set.'))
        Email = company.email
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            ContattiTrasmittente = ContattiTrasmittenteType(
                Telefono=Telefono, Email=Email)

        return True

    def checkSetupPhone(self, phone_number=False):
        if phone_number and '+' in phone_number:
            phone_number = phonenumbers.format_number(
                phonenumbers.parse(phone_number),
                phonenumbers.PhoneNumberFormat.NATIONAL)
        return phone_number

    def _setContatti(self, CedentePrestatore, company):
        CedentePrestatore.Contatti = ContattiType(
            Telefono=self.checkSetupPhone(company.partner_id.phone) or None,
            Fax=self.checkSetupPhone(company.partner_id.fax) or None,
            Email=company.partner_id.email or None
            )
