# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order general discount exclude',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'summary': 'Add ability to exclude product from discount in sales.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_general_discount',
    ],
    'data': [
        'views/product_template.xml',
    ],
    'installable': True,
}
