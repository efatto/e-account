# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'MIS Builder MRP cash flow',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Generate automatically cash flow lines from MRP line.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'mis_builder_cash_flow_inheritable',
        'account_payment_partner',
        'mrp',
        'mrp_bom_evaluation',
        'mrp_production_manual_procurement',
        'purchase_last_price_info',
    ],
    'data': [
        'views/stock_move.xml',
        'views/cashflow_line.xml',
    ],
    'installable': True,
    'post_init_hook': 'create_cashflow_lines',
}
