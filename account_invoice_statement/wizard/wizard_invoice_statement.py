# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, exceptions, _
from ..bindings.invoice_statement_v_2_0 import (
    AltriDatiIdentificativiNoCAPType,
    AltriDatiIdentificativiNoSedeType,
    CaricaType,
    CedentePrestatoreDTRType,
    CessionarioCommittenteDTRType,
    DatiFattura,
    DatiFatturaBodyDTRType,
    DatiFatturaHeaderType,
    DatiFatturaType,
    DatiGeneraliDTRType,
    DatiIVAType,
    DatiRiepilogoType,
    DichiaranteType,
    DTEType,
    DTRType,
    IdentificativiFiscaliType,
    IdentificativiFiscaliITType,
    IdFiscaleITType,
    IdFiscaleType,
    IndirizzoNoCAPType,
    TipoDocumentoType,
)
import base64
import logging
_logger = logging.getLogger(__name__)

try:
    from unidecode import unidecode
    from pyxb.exceptions_ import SimpleFacetValueError, SimpleTypeValueError
except ImportError as err:
    _logger.debug(err)

import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class WizardInvoiceStatement(models.TransientModel):
    _name = "wizard.invoice.statement"
    _description = "Export invoice statement"

    def __init__(self, pool, cr):
        self.statement = False
        super(WizardInvoiceStatement, self).__init__(pool, cr)

    def get_date_start_stop(self, statement):
        date_start = False
        date_stop = False
        for period in statement.period_ids:
            if not date_start:
                date_start = period.date_start
            else:
                if period.date_start < date_start:
                    date_start = period.date_start
            if not date_stop:
                date_stop = period.date_stop
            else:
                if period.date_stop > date_stop:
                    date_stop = period.date_stop
        date_start = datetime.datetime.strptime(date_start,
                                                DEFAULT_SERVER_DATE_FORMAT)
        date_stop = datetime.datetime.strptime(date_stop,
                                               DEFAULT_SERVER_DATE_FORMAT)
        return date_start, date_stop

    def saveAttachment(self, company_vat, progressive_number):
        attach_obj = self.env['invoice.statement.attachment']
        attach_vals = {
            'name': '%s_%s.xml' % (company_vat, str(progressive_number)),
            'datas_fname': '%s_%s.xml' % (company_vat, str(progressive_number)),
            'datas': base64.encodestring(self.statement.toxml("latin1")),
        }
        attach_id = attach_obj.create(attach_vals)

        # vat_settlement_xml = settlement.toDOM().toprettyxml(encoding="latin1")
        # fn_name = 'LiquidazioneIVA-%05d.xml' % progressivo_telematico
        # fn_name = 'IT%s_LI_%05d.xml' % (vat, progressivo_telematico)
        # attach_vals = {
        #     'name': fn_name,
        #     'datas_fname': fn_name,
        #     'datas': base64.encodestring(vat_settlement_xml),
        #     'res_model': 'account.vat.period.end.statement',
        #     'res_id': statement.id
        # }

        return attach_id

    @api.multi
    def export_invoice_statement(self):
        invoice_statement_obj = self.env['invoice.statement']
        statement_id = invoice_statement_obj.browse(
            self._context.get('active_id', False))

        # get company vat and fiscalcode
        company = statement_id.company_id
        if company.partner_id.vat[:2].lower() == 'it':
            company_vat = company.partner_id.vat[2:]
        else:
            company_vat = company.partner_id.vat
        if company.partner_id.fiscalcode:
            if len(company.partner_id.fiscalcode) == 16:
                company_fiscalcode = company.partner_id.fiscalcode
            else:
                company_fiscalcode = company.partner_id.fiscalcode[2:]
        else:
            company_fiscalcode = company_vat

        # get data for statement
        date_start, date_stop = self.get_date_start_stop(statement_id)
        progressive_number = invoice_statement_obj.search(
            [], order='progressive_number desc', limit=1).progressive_number

        # create container object Statement
        self.statement = DatiFattura(versione='DAT20') #(DatiFatturaType())
        self.statement.DatiFatturaHeader = (DatiFatturaHeaderType())
        self.statement.DatiFatturaHeader.ProgressivoInvio = str(progressive_number + 1)

        #get invoice for date of period selected

        ###### DTR - INVOICE RECEIVED ######
        if statement_id.type == 'DTR':
            invoice_ids = self.env['account.invoice'].search([
                # ('period_id', 'in', statement_id.period_ids)
                ('registration_date', '>=', date_start),
                ('registration_date', '<=', date_stop),
                ('type', 'in', ['in_invoice', 'in_refund']),
            ])
            #todo group invoices by partner (limit 1000)
            partner_ids = invoice_ids.mapped('partner_id')
            if partner_ids:
                #### CESSIONARIO - COMMITTENTE DTR ####
                self.statement.DTR = (DTRType())
                #TODO INSERIRE I DATI DEL MITTENTE - 1 BLOCCO SINGOLO
                self.statement.DTR.CessionarioCommittenteDTR = (CessionarioCommittenteDTRType())
                self.statement.DTR.CessionarioCommittenteDTR.IdentificativiFiscali = (IdentificativiFiscaliITType())
                self.statement.DTR.CessionarioCommittenteDTR.IdentificativiFiscali.IdFiscaleIVA = (IdFiscaleITType())
                self.statement.DTR.CessionarioCommittenteDTR.IdentificativiFiscali.IdFiscaleIVA.IdPaese = 'IT'
                self.statement.DTR.CessionarioCommittenteDTR.IdentificativiFiscali.IdFiscaleIVA.IdCodice = company_vat
            missing_vat_partners = []
            for partner in partner_ids:
                # report this to the user to fix partners
                if not partner.vat:
                    missing_vat_partners.append(partner.name)
                    continue
                # exclude vat != it
                if partner.vat and partner.vat[:2].upper() != 'IT':
                    continue
                # TODO qui si creano piu blocchi, uno per ogni partner
                CedentePrestatoreDTR = CedentePrestatoreDTRType()
                CedentePrestatoreDTR.IdentificativiFiscali = (IdentificativiFiscaliType())
                CedentePrestatoreDTR.IdentificativiFiscali.IdFiscaleIVA = (IdFiscaleType())
                # butta li tanto per fare

                CedentePrestatoreDTR.IdentificativiFiscali.IdFiscaleIVA.IdPaese = partner.vat[:2]
                CedentePrestatoreDTR.IdentificativiFiscali.IdFiscaleIVA.IdCodice = partner.vat[2:]
                fiscalcode = False
                if partner.fiscalcode:
                    if len(partner.fiscalcode) == 16:
                        fiscalcode = partner.fiscalcode
                    if len(partner.fiscalcode) == 13:
                        fiscalcode = partner.fiscalcode[2:]
                if fiscalcode:
                    CedentePrestatoreDTR.IdentificativiFiscali.CodiceFiscale = fiscalcode
                CedentePrestatoreDTR.AltriDatiIdentificativi = (AltriDatiIdentificativiNoCAPType())
                if not partner.is_company:
                    CedentePrestatoreDTR.AltriDatiIdentificativi.Nome = partner.first_name
                    CedentePrestatoreDTR.AltriDatiIdentificativi.Cognome = partner.last_name
                else:
                    CedentePrestatoreDTR.AltriDatiIdentificativi.Denominazione = partner.name
                CedentePrestatoreDTR.AltriDatiIdentificativi.Sede = (IndirizzoNoCAPType())
                CedentePrestatoreDTR.AltriDatiIdentificativi.Sede.Indirizzo = partner.street or ''
                CedentePrestatoreDTR.AltriDatiIdentificativi.Sede.CAP = partner.zip or ''
                CedentePrestatoreDTR.AltriDatiIdentificativi.Sede.Comune = partner.city or ''
                CedentePrestatoreDTR.AltriDatiIdentificativi.Sede.Provincia = partner.state_id.code if partner.state_id else ''
                CedentePrestatoreDTR.AltriDatiIdentificativi.Sede.Nazione = partner.country_id.code if partner.country_id else 'IT'
                for invoice in invoice_ids.filtered(
                        lambda x: x.partner_id == partner):
                    #todo get invoice tax
                    DatiFatturaBodyDTR = DatiFatturaBodyDTRType()
                    DatiFatturaBodyDTR.DatiGenerali = (DatiGeneraliDTRType())
                    DatiFatturaBodyDTR.DatiGenerali.TipoDocumento = u'TD01'
                    DatiFatturaBodyDTR.DatiGenerali.Data = invoice.date_invoice
                    DatiFatturaBodyDTR.DatiGenerali.Numero = invoice.supplier_invoice_number
                    DatiFatturaBodyDTR.DatiGenerali.DataRegistrazione = invoice.registration_date
                    for invoice_tax in invoice.tax_line:
                        #todo add line...
                        DatiRiepilogo = DatiRiepilogoType()
                        DatiRiepilogo.ImponibileImporto = '%.2f' % invoice_tax.base
                        DatiRiepilogo.DatiIVA = (DatiIVAType())
                        DatiRiepilogo.DatiIVA.Imposta = '%.2f' % invoice_tax.amount
                        DatiRiepilogo.DatiIVA.Aliquota = '%.2f' % invoice_tax.tax_amount #factor_tax?
                        # DatiRiepilogo.Natura = se non iva
                        DatiRiepilogo.EsigibilitaIVA = 'I'
                        DatiFatturaBodyDTR.DatiRiepilogo.append(DatiRiepilogo)
                    CedentePrestatoreDTR.DatiFatturaBodyDTR.append(DatiFatturaBodyDTR)
                self.statement.DTR.CedentePrestatoreDTR.append(CedentePrestatoreDTR)


        #('type', 'in', ['out_invoice', 'out_refund']),
        # todo ESCLUDERE AUTOFATTURE
        #auto_invoice_id nella fatture fornitori non c'è

        #
        #     _logger.debug(settlement.Intestazione.toDOM().toprettyxml(
        #         encoding="latin1"))
        #     if statement.codice_carica:
        #         if statement.codice_carica != '0':
        #             settlement.Comunicazione.Frontespizio.CFDichiarante = \
        #                 statement.soggetto_codice_fiscale
        #             settlement.Comunicazione.Frontespizio.CodiceCaricaDichiarante = \
        #                 statement.codice_carica
        #         elif not statement.incaricato_trasmissione_codice_fiscale:
        #             settlement.Comunicazione.Frontespizio.CodiceFiscale = \
        #                 statement.soggetto_codice_fiscale


        #     settlement.Comunicazione.DatiContabili.Modulo.append(modulo)
        #
        #     _logger.debug(settlement.Comunicazione.DatiContabili.toDOM().toprettyxml(encoding="latin1"))
        #
        #     settlement.Comunicazione.identificativo = \
        #         "%05d" % progressivo_telematico
        #
        statement_id.write(
            {'progressive_number': progressive_number})
        try:
            attach_id = self.saveAttachment(company_vat, progressive_number)
        except (SimpleFacetValueError, SimpleTypeValueError) as e:
            raise exceptions.ValidationError(
                _("XML SDI validation error"),
                (unicode(e)))
        view_rec = self.env['ir.model.data'].get_object_reference(
            'account_invoice_statement',
            'view_invoice_statement_attachment_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False
        return {
            'view_type': 'form',
            'name': "Export Invoice Statement",
            'view_id': [view_id],
            'res_id': attach_id.id,
            'view_mode': 'form',
            'res_model': 'invoice.statement.attachment',
            'type': 'ir.actions.act_window',
            'context': self._context,
        }
