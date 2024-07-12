# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account invoice request confirm on fiscal document",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": """
    Add confirm request if out invoice fiscal document type is not the default one.
    """,
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "depends": [
        "account",
        "l10n_it_fiscal_document_type",
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "installable": True,
}
