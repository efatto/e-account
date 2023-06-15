# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Sale order date visibility",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Move date_order for quotation in header for better visibility "
    "with opportunity, client order ref, project and analytic.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "sale_crm",
        "sale_timesheet",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
