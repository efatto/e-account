# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Vat statement report layouted',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'description': 'Vat statement report layouted',
    'depends': [
        'account_vat_period_end_statement',
    ],
    'data': [
        'views/report_vatperiodendstatement.xml',
    ],
    'installable': True,
}