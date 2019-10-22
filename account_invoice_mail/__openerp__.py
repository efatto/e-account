# -*- coding: utf-8 -*-
# Copyright 2017-2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Account invoice mail',
    'version': '8.0.1.1.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Button to send mail for invoice always visible.'
                   'Add field Invoice Email for simpler management.',
    'website': 'http://www.efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
    ],
    'external_dependencies': {
        'python': [
            'email_validator',
        ],
    },
    'installable': True
}
