# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale order margin state",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Add state of margin in sale order line.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "sale_margin",
    ],
    "data": [
        "views/res_config_settings_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
