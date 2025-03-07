# Copyright 2018 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Export e-invoice report in zip file',
    'version': '14.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add ability to export more report of e-invoice in a zip file.',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_fatturapa_in',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard_export.xml',
    ],
    'installable': True
}
