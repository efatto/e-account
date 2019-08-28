# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2018 MuK IT GmbH
# Copyright 2019 Enrico Ganzaroli (enrico.gz@gmail.com)
# Copyright 2019 Sergio Corato (https://efatto.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Pre-configurable Import CSV/XLS/XLSX/ODS Bank Statement",
    "summary": """Bank Statement Import Wizard""",
    "version": "10.0.1.1.4",
    "category": "Accounting",
    "license": "AGPL-3",
    "website": "https://efatto.it",
    "author": "MuK IT",
    "contributors": [
        "Mathias Markl <mathias.markl@mukit.at>, "
        "Enrico Ganzaroli, Sergio Corato",
    ],
    "depends": [
        "base_import",
        "account_bank_statement_import", 
    ],
    "data": [
        "template/assets.xml",
        "views/bank_view.xml",
        "views/account_bank_statement_import_views.xml"
    ],
    "installable": True,
}