# Copyright 2019-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fattura elettronica - Integrazione SO",
    "summary": "Modulo ponte tra emissione fatture elettroniche e dati "
               "ordine di vendita",
    "version": "12.0.1.0.1",
    "development_status": "Beta",
    "category": "Hidden",
    "website": "https://github.com/sergiocorato/e-account",
    "author": "Sergio Corato",
    "maintainers": ["sergiocorato"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "depends": [
        "l10n_it_fatturapa_out",
        "sale",
        "stock_picking_invoice_link",
    ],
    "data": [
        "views/partner_view.xml",
        "views/account_view.xml",
        "views/company_view.xml",
    ],
}
