# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Sale order view usability',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': '''
This module extend sale order views with:
-----------------------------------------
* add sale order ref, origin and total amount in tree view,
* add sale order ref in form view,
* show origin field to base user.''',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'LGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
