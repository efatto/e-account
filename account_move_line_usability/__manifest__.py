# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Account move line usability',
    'version': '12.0.1.0.1',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'description': '''
Solve some usability issue in account move line:
------------------------------------------------
* set credit accordingly to debit and viceversa,
* add filter from_date and to_date,
* set minimum width for account fields,
* set next line with balance value,
* set account accordingly to partner.
''',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/css.xml',
        'views/account.xml',
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
