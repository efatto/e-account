# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase order line planned payments',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add payment datas to purchase order line computed from planned '
                   'date.',
    'website': 'https://efatto.it',
    'depends': [
        'account',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase.xml',
    ],
    'installable': True,
}
