# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Update discount in invoice',
    'version': '12.0.1.0.2',
    'category': 'Invoice Management',
    'license': 'AGPL-3',
    'description': """
    Add the ability to update discount in all invoice lines with a button.
    """,
    'author': "Sergio Corato",
    'website': 'https://efatto.it',
    'depends': [
        'account',
    ],
    'data': [
        'views/invoice_view.xml',
    ],
    'installable': True,
}
