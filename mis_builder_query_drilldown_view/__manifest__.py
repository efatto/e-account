# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mis builder analytic view",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "author": "Sergio Corato",
    "website": "https://efatto.it",
    "license": "AGPL-3",
    "summary": "Add custom analytic view to mis report",
    "depends": ["mis_builder_analytic_query",
                "mis_builder_query_drilldown",
                "account_invoice_line_usability",
                # "account_analytic_line_usability",
                "sale_order_line_usability",
                ],
    "data": ["views/account.xml", "views/sale.xml"],
    "installable": True,
    "maintainers": ["sergiocorato"],
}
