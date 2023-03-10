# Copyright 2018-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Partner vat or fiscalcode required if no contact',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Partner vat or fiscalcode required if no contact. '
                   'Remove quick-create from sale - purchase order to put '
                   'required only in view.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_fiscalcode',
        'purchase',
        'sale',
    ],
    'data': [
        'views/partner.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
    ],
    'installable': True
}
