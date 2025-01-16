# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account invoice Intrastat info",
    "summary": "Add Intrastat info to invoice narration",
    "version": "14.0.1.0.1",
    "category": "Accounting",
    "website": "https://github.com/efatto/e-account",
    "author": "Sergio Corato",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "l10n_it_fatturapa_out",
        "l10n_it_intrastat",
        "mrp",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
}
