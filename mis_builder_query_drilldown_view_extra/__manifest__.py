# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mis builder drilldown view analytic extra cost",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "summary": "Add analytic extra cost to drilldown view to mis report",
    "depends": [
        "account_analytic_mrp_extra_cost",
        "mis_builder_query_drilldown_view",
    ],
    "data": [
        "views/account.xml",
    ],
    "installable": True,
}
