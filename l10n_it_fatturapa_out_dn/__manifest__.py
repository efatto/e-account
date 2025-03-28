# Copyright 2018 Lorenzo Battistini
# Copyright 2018 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# Copyright 2018 Ruben Tonetto (Associazione PNLUG - Gruppo Odoo)
# Copyright 2025 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'ITA - Fattura elettronica - Integrazione DN',
    "summary": "Modulo ponte tra emissione fatture elettroniche e DN",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    'website': 'https://github.com/efatto/e-account'
               '/tree/12.0/l10n_it_fatturapa_out_dn',
    "author": "Sergio Corato",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "l10n_it_fatturapa_out",
        "l10n_it_delivery_note",
    ],
    "data": [
        "wizard/wizard_export_fatturapa_view.xml",
        "views/account_invoice.xml",
    ],
}
