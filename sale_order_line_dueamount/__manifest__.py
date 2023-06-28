# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale order line planned payments',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add payment datas to sale order line computed from commitment '
                   'date.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'sale_management',
        'sale_order_line_date',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale.xml',
    ],
    'installable': True,
    # 'post_init_hook': 'create_dueamount',
}
