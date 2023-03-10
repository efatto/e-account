# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale project visibility',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Move opportunity, project and analytic for quotation in header '
                   'for better visibility.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale_crm',
        'sale_timesheet_existing_project',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
