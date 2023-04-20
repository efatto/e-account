# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale order revision analytic',
    'version': '12.0.1.0.0',
    'category': 'Sale Management',
    'author': 'Sergio Corato',
    'description': 'The default behaviour of sale order revision create a new analytic '
                   'account for each revision. '
                   'This module set the same analytic account on revisioned sale order '
                   'as the original sale order, to do not create duplicated accounts.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_revision',
        'sale_timesheet',
    ],
    'data': [
    ],
    'installable': True,
}
