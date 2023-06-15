# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Sale order project, analytic and opportunity visibility",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Move project, opportunity and analytic for quotation in header.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "sale_crm",
        "sale_date_order_visibility",
        "sale_timesheet",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
