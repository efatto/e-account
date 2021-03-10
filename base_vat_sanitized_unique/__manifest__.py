# Copyright 2017-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base VAT Sanitized Unique',
    'version': '12.0.1.0.3',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'description': 'Add constrains to sanitized VAT number and fiscalcode field for '
                   'unique consistency.',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'base_vat_sanitized',
    ],
    'installable': True,
}
