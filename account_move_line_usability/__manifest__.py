# Copyright 2017-2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account move line usability",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Sergio Corato",
    "summary": """
Solve some usability issue in account move line: add filter from_date and to_date,
 set minimum width for account fields, set account accordingly to partner.
""",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/css.xml",
        "views/account.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
