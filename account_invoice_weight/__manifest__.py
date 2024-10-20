# Copyright 2017 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account invoice weight",
    "version": "14.0.1.0.1",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "This module change to computed shipping fields in account invoice: "
    "weight, net weight, packages and volume.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_shipping_info",
        "delivery_package_number",
        "product_logistics_uom",
        "stock_picking_invoice_link",
        "stock_picking_packages",
        "stock_picking_volume",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "installable": True,
    "pre_init_hook": "migrate_fields",
}
