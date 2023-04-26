# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase order forecast cashflow',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Generate cashflow lines from purchase order line with payment and '
                   'planned date.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'mis_builder_cash_flow',
        'account_payment_purchase',
        'purchase',
    ],
    'data': [
        'views/purchase.xml',
        'views/cashflow_line.xml',
    ],
    'installable': True,
    'post_init_hook': 'create_cashflow_lines',
}
