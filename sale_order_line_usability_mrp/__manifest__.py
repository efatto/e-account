# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order line usability MRP',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'summary': 'Autoinstall module to fix computation on mrp.',
    'website': 'https://github.com/efatto/e-account',
    'license': 'AGPL-3',
    'depends': [
        'mrp_bom_sale_pricelist',
        'sale_order_line_usability',
    ],
    'data': [
    ],
    'installable': True,
    'auto_install': True,
}
