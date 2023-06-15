# Copyright 2017-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale order line menu usability",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "This module extend menu for uninvoiced order lines.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "sale_backorder",
        "sale_order_line_date",
    ],
    "data": [
        "views/sale.xml",
    ],
    "installable": True,
}
