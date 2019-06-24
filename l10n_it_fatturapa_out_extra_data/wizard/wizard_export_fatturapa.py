# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openerp import models
from openerp.addons.l10n_it_fatturapa.bindings.fatturapa_v_1_2 import (
    AltriDatiGestionaliType
)


class WizardExportFatturapa(models.TransientModel):
    _inherit = "wizard.export.fatturapa"

    def setDettaglioLinea(
            self, line_no, line, body, price_precision, uom_precision):
        res = super(WizardExportFatturapa, self).setDettaglioLinea(
            line_no, line, body, price_precision, uom_precision)
        dati_gestionali_list = []
        # add VAT
        dati_gestionali = AltriDatiGestionaliType()
        tax_description = line.invoice_line_tax_id[0].description
        dati_gestionali.TipoDato = tax_description[:10]
        dati_gestionali.RiferimentoTesto = 'VAT'
        dati_gestionali_list.append(dati_gestionali)
        # add category
        if line.product_id:
            categ_id = line.product_id.categ_id
            while categ_id.parent_id:
                categ_id = categ_id.parent_id
            dati_gestionali = AltriDatiGestionaliType()
            dati_gestionali.TipoDato = categ_id.name[:10]
            dati_gestionali.RiferimentoTesto = 'CAT'
            dati_gestionali_list.append(dati_gestionali)

        # get dettagliolinea for actual row
        DettaglioLinea = [x for x in body.DatiBeniServizi.DettaglioLinee if
                          x.NumeroLinea == line_no]
        if DettaglioLinea:
            for dati_gestionali in dati_gestionali_list:
                DettaglioLinea[0].AltriDatiGestionali.append(
                    dati_gestionali
                )
        return res
