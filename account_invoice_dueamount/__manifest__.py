# Copyright 2017-2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Account invoice due amount',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'This module add optional custom due amount field, '
                   'to customize amount and dates of payments.',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
