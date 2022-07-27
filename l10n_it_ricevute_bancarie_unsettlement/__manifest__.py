# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "ITA - Ricevute bancarie smarca pagamento",
    "summary": "Annulla l\"effetto del bottone marca come pagata",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://efatto.it",
    "author": "Sergio Corato",
    "maintainers": ["sergiocorato"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "l10n_it_ricevute_bancarie",
    ],
    "data": [
        "views/riba_view.xml",
    ],
}
