# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'E-invoice received date editable',
    'version': '12.0.1.0.0',
    'category': 'Invoice Management',
    'license': 'AGPL-3',
    'summary': "Add the ability to always set e-invoice received date",
    'author': "Sergio Corato",
    'website': 'https://github.com/sergiocorato/e-account',
    'depends': [
        'l10n_it_fatturapa_in',
    ],
    'data': [
        'views/invoice_view.xml',
    ],
    'installable': True,
}
