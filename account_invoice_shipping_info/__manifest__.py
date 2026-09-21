# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Add shipping info to invoice",
    "version": "18.0.1.0.0",
    "category": "Invoice Management",
    "license": "AGPL-3",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "depends": [
        "account",
        "l10n_it_delivery_note",
        "l10n_it_accompanying_invoice",
    ],
    "data": [
        "views/invoice_view.xml",
    ],
    "installable": True,
}
