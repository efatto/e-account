# -*- coding: utf-8 -*-
# Copyright 2017-2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Account invoice mail address',
    'version': '8.0.1.1.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add field Invoice Email - checked with email_validator - '
                   'for simpler management.',
    'website': 'http://www.efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    'external_dependencies': {
        'python': [
            'email_validator',
        ],
    },
    'installable': True
}
