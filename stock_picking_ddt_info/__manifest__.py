# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Add DDT vendor info to incoming picking DEPRECATED",
    "version": "14.0.1.0.0",
    "category": "Stock Management",
    "license": "AGPL-3",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "summary": "Da migrare i campi all'interno del modulo l10n_it_delivery_note,"
               "in cui ci sono uguali con il prefisso dn_, verificare solo "
               "dove si vedono a video.",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock.xml",
    ],
    "installable": True,
}
