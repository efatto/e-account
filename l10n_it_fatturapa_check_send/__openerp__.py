# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Check invoice send to SdI',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'This module add a check to period to disable sending '
                   'invoice to foreign customer to SdI (sent only for fiscal reason).',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    'depends': [
        'l10n_it_fatturapa_out',
        'l10n_it_fatturapa_pec',
    ],
    'data': [
        'views/account.xml',
    ],
    'installable': True
}
