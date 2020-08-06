# Copyright 2013-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Fiscal Year Closing journal data',
    'version': '12.0.1.0.0',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'category': 'Generic Modules/Accounting',
    'description': 'Fiscal Year Closing journal data',
    'license': 'AGPL-3',
    'depends': [
        'account_fiscal_year_closing',
    ],
    'data': [
        'data/account_journal.xml',
    ],
    'installable': True,
}
