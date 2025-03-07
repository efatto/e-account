# Copyright 2018 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Export e-invoice report in ZIP file",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "description": "Export several report of e-invoice in a ZIP file.",
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
