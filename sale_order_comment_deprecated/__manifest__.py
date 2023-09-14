# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale date deprecated comment preserve",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "summary": "This module only preserve fields removed from v.>12.0: note1 and note2 "
               "in sale order (comment top and bottom now linked with a m2o) and "
               "formatted_note in sale order line (now unexisting), in readonly view.",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
