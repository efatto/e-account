# Copyright 2025 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Export translation",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Export translation in xlsx file in attachment.",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "report_xlsx",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/translation_export.xml",
        "reports/xlsx_translation_export.xml",
        "data/cron.xml",
    ],
    "installable": True,
}
