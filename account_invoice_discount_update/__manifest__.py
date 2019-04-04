# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2016-2018 Sergio Corato
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
    'name': 'Update discount in invoice',
    'version': '10.0.1.0.1',
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
