# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'E-invoice advance auto',
    'version': '8.0.1.0.0',
    'category': 'Sale',
    'author': 'Sergio Corato',
    'description': 'Add boolean to mark advance invoices when they are created'
                   ' from sale order',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'l10n_it_fiscal_document_type',
        'sale',
    ],
    'data': [
        'views/account.xml',
    ],
    'installable': True
}
