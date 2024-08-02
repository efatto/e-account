# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice price unit net",
    "summary": "Modulo che aggiunge la possibilità di stampare ed esportare i prezzi "
               "al netto dello sconto, senza mostrare lo sconto",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Hidden",
    "website": "https://github.com/sergiocorato/e-account",
    "author": "Sergio Corato",
    "maintainers": ["sergiocorato"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "depends": [
        "account_invoice_triple_discount",
        "l10n_it_fatturapa_out",
        "sale",
    ],
    "data": [
        "views/partner_view.xml",
        "views/account_view.xml",
        "views/company_view.xml",
    ],
}
