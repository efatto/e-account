# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale crm view usability',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'author': 'Sergio Corato',
    'description': 'This module extend sale order showing sale order button even if '
                   'amount is zero',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale_crm',
    ],
    'data': [
        'views/crm_lead_view.xml',
    ],
    'installable': True,
}
