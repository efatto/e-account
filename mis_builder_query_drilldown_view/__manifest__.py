# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mis builder drilldown view",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "summary": "Add drilldown views to mis report",
    "depends": [
        "account_invoice_line_usability",
        "mis_builder_query_drilldown",
        "mrp",
        "mrp_workorder_timesheet_cost",
        "mrp_workcenter_productivity_usability",
        "sale_order_line_usability",
        "purchase_stock",
        "stock_move_usability",
    ],
    "data": [
        "views/account.xml",
        "views/mrp.xml",
        "views/purchase.xml",
        "views/sale.xml",
        "views/stock.xml",
    ],
    "installable": True,
    "maintainers": ["sergiocorato"],
}
