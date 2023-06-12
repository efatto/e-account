# Copyright 2020-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Update discount in invoice",
    "version": "14.0.1.0.0",
    "category": "Invoice Management",
    "license": "AGPL-3",
    "description": """
    Add the ability to update discount in all invoice lines with a button.
    """,
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "depends": [
        "account",
    ],
    "data": [
        "views/invoice_view.xml",
    ],
    "installable": True,
}
