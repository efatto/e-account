# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'MIS Builder cash flow make query inheritable',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'This module do nothing by himself. It is used from other modules '
                   'to extend cash flow query.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'mis_builder_cash_flow',
    ],
    'data': [
        'report/mis_cash_flow_views.xml',
    ],
    'installable': True,
}
