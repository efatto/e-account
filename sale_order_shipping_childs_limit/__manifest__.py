# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Sale order limit shipping to childs',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': '''
This module extend sale order views with:
-----------------------------------------
* limit domain of shipping partner to partner and its children.''',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
