
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.addons.l10n_it_account.tools.account_tools import encode_for_export
from odoo.addons.l10n_it_fatturapa.bindings.fatturapa import (
    DatiDDTType,
    DatiTrasportoType,
    DatiAnagraficiVettoreType,
    IndirizzoType,
    IdFiscaleType,
    AnagraficaType
)


class WizardExportFatturapa(models.TransientModel):
    _inherit = "wizard.export.fatturapa"

    include_ddt_data = fields.Selection([
        ('dati_ddt', 'Include TD Data'),
        ('dati_trasporto', 'Include transport data'),
        ],
        string="TD Data",
        help="Include TD data: The field must be entered when a transport "
             "document associated with a deferred invoice is present\n"
             "Include transport data: The field must be entered when a "
             "accompanying invoice to be filled with transport data is present"
    )

    def setDatiDDT(self, invoice, body):
        res = super().setDatiDDT(
            invoice, body)
        if self.include_ddt_data == 'dati_ddt':
            # fattura differita
            inv_lines_by_ddt = {}
            for line in invoice.invoice_line_ids:
                if (
                    line.delivery_note_id and
                    line.delivery_note_id.name and
                    line.delivery_note_id.date
                ):
                    key = (
                        line.delivery_note_id.name,
                        line.delivery_note_id.date
                    )
                    if key not in inv_lines_by_ddt:
                        inv_lines_by_ddt[key] = []
                    inv_lines_by_ddt[key].append(line.ftpa_line_number)
            for key in sorted(inv_lines_by_ddt.keys()):
                DatiDDT = DatiDDTType(
                    NumeroDDT=key[0],
                    DataDDT=key[1]
                )
                for line_number in inv_lines_by_ddt[key]:
                    DatiDDT.RiferimentoNumeroLinea.append(line_number)
                body.DatiGenerali.DatiDDT.append(DatiDDT)
        elif self.include_ddt_data == 'dati_trasporto':
            # fattura immediata
            body.DatiGenerali.DatiTrasporto = DatiTrasportoType(
            )
            carrier_id = invoice.carrier_id
            if carrier_id:
                if not carrier_id.vat:
                    raise UserError(
                        _('TIN not set for %s.') % carrier_id.name)
                body.DatiGenerali.DatiTrasporto.DatiAnagraficiVettore = (
                    DatiAnagraficiVettoreType())
                if carrier_id.fiscalcode:
                    body.DatiGenerali.DatiTrasporto.DatiAnagraficiVettore.\
                        CodiceFiscale = carrier_id.fiscalcode
                body.DatiGenerali.DatiTrasporto.DatiAnagraficiVettore.\
                    IdFiscaleIVA = IdFiscaleType(
                        IdPaese=carrier_id.vat[0:2],
                        IdCodice=carrier_id.vat[2:]
                    )
                body.DatiGenerali.DatiTrasporto.DatiAnagraficiVettore.\
                    Anagrafica = AnagraficaType(
                        Denominazione=carrier_id.name)
                body.DatiGenerali.DatiTrasporto.IndirizzoResa = (
                    IndirizzoType(
                        Indirizzo=encode_for_export(carrier_id.street, 60),
                        CAP=carrier_id.zip,
                        Comune=encode_for_export(carrier_id.city, 60),
                        Provincia=carrier_id.state_id.code,
                        Nazione=carrier_id.country_id.code,
                    )
                )
        return res
