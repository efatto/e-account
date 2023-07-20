# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Product excluded from sale margin',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'summary': 'Add ability to exclude products from margin computation.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_margin_percent',
    ],
    'data': [
        'views/product_template.xml',
    ],
    'installable': True,
}
