# Copyright (C) 2015 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Partner button view account moves',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Alexis de Lattre - Akretion, Sergio Corato',
    'description': 'With this module partner will have button with '
                   'only account moves linked to account.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/partner_account_view.xml',
    ],
    'installable': True,
}
