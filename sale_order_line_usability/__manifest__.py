# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale order line usability',
    'version': '12.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add order line product standard price link.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'delivery',
        'sale_stock',
    ],
    'data': [
        'views/sale_order_line_views.xml',
    ],
    'installable': True,
}
