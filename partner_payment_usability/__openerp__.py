# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Sergio Corato
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Partner payment view usability',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules',
    'website': 'https://www.efatto.it',
    "author": "Sergio Corato",
    'description': 'Partner payment remove selection widget because '
                   'limited to 100 records.',
    'depends': [
        'account',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'installable': False,
}
