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
    'name': 'Sale advance invoice extension with SAL',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'Add ability to get description from sale order during'
                   ' advance invoice creation, with contract SAL.',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'sale_advance_invoice',
        'account_analytic_sal',
    ],
    'data': [
        'views/sale.xml',
    ],
    'installable': False
}
