# Copyright (C) 2015 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Forbid deactivation partner with invoices or moves",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Sergio Corato",
    "summary": "This module stop the user to deactivate partners that have "
               "invoices or moves. This would make impossible to find the "
               "invoices/moves without knowing their exact number.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
    ],
    "installable": True,
}
