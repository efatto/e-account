# -*- coding: utf-8 -*-
# Copyright (C) 2017-2019 Sergio Corato
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl
{
    'name': 'Account invoice due amount',
    'version': '10.0.1.0.2',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'This module add optional custom due amount field, '
                   'to customize amount and dates of payments.',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
