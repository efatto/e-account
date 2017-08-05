# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2017 Sergio Corato
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'IVP 2017',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'IVP 2017 export xml file',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'account',
        'account_vat_period_end_statement',
        'account_vat_statement_endyear',
        'l10n_it_vat_registries',
        'l10n_it_fiscalcode',
    ],
    'data': [
        'views/account_view.xml',
        'wizard/vat_settlement.xml',
    ],
    'external_dependencies': {
        'python': ['pyxb'],
    },
    'installable': True
}
