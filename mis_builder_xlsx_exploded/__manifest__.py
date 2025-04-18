# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mis builder exploded XLS",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "summary": "Add XLS report with extended details to mis report",
    "depends": ["mis_builder"],
    "data": [
        "views/mis_report.xml",
        "report/mis_report_exploded_xlsx.xml",
    ],
    "installable": True,
    "maintainers": ["sergiocorato"],
    "qweb": ["static/src/xml/mis_report_widget.xml"],
}
