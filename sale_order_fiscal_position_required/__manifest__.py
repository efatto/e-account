# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order fiscal position required',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'summary': 'Set required to fiscal position field on sale order view where in '
               '"sale" state.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': True,
}
