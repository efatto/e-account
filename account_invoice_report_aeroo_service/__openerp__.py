# -*- coding: utf-8 -*-
#
#    Copyright (C) 2013-2014 Didotech Srl (<http://www.didotech.com>)
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
    'name': 'Aeroo invoice report template service',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'website': 'http://www.efatto.it',
    'description': 'Aeroo invoice report template for service companies.',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'report_aeroo_parser',
    ],
    'data': [
        'data/reports.xml',
    ],
    'installable': True
}