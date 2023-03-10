# Copyright 2017-2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sequence access to accountant',
    'version': '12.0.1.0.0',
    'category': 'other',
    'description': 'Add ability to modify sequence from accountant users',
    'author': 'Sergio Corato',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
