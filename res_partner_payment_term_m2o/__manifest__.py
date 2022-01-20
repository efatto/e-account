# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Partner payment term m2o',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'description': 'With this module partner will have normal selection of '
                   'payment term.',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account_payment_partner',
    ],
    'data': [
        'views/partner_account_view.xml',
    ],
    'installable': True,
}
