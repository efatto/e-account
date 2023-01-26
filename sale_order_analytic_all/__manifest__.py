# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale order analytic all',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Simple module that create analytic account, procurement group and '
                   'project for every order at creation, even without lines. Added '
                   'service later will create task in the same project.',
    'website': 'https://efatto.it',
    'depends': [
<<<<<<< HEAD
<<<<<<< HEAD
        'sale_stock',
=======
        # 'purchase_stock',
        'sale_stock',
        # 'stock_dropshipping',
>>>>>>> [FIX] comment not-verified import
=======
        'sale_stock',
        'sale_timesheet',
        'sale_timesheet_existing_project',
>>>>>>> [IMP] create project at SO creation
    ],
    'data': [
    ],
    'installable': True,
}
