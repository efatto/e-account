# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Update invoice line",
    "version": "14.0.1.0.0",
    "category": "Invoice Management",
    "license": "AGPL-3",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "depends": [
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/update_account_move_line.xml",
        "views/invoice_view.xml",
    ],
    "installable": True,
}
