# Copyright 2018 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Export e-invoice preview in ZIP file",
    "version": "16.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "depends": [
        "l10n_it_fatturapa_in",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/wizard_export.xml",
    ],
    "installable": True,
}
