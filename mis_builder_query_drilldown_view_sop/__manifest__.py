# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mis builder drilldown view sop",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "summary": "Add drilldown sale order progress views to mis report",
    "depends": [
        "mis_builder_query_drilldown_view",
        "sale_order_progress",
    ],
    "data": [
        "views/sale_order_progress.xml",
    ],
    "installable": True,
    "auto_install": True,
    "maintainers": ["sergiocorato"],
}
