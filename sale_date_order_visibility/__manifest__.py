# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale date order visibility',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Move date_order and client order ref for quotation in header for '
                   'better visibility.',
    'website': 'https://efatto.it',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
