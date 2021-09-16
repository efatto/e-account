# Copyright 2017-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Partner phone, mobile or email required in sale order creation',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'When creating a partner directly from a sale order, '
                   'phone, mobile or email are required with this module. '
                   'Partner cannot be created quickly - e.g. only with name.',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'sale',
    ],
    'data': [
        'views/partner.xml',
        'views/sale_order.xml',
    ],
    'installable': True
}
