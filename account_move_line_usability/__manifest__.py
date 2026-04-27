# Copyright 2017 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account move line usability",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/account.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_move_line_usability/static/src/scss/account.scss"
        ],
    },
    "installable": True,
}
