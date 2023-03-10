# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Create invoice payments from xml',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Use payments info received in e-invoice to create payments.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'account_invoice_dueamount',
        'l10n_it_fatturapa_in',
    ],
    'data': [
    ],
    'installable': True,
}
