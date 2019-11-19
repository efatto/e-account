# -*- coding: utf-8 -*-
#
#    Copyright (C) 2013-2014 Didotech Srl (<http://www.didotech.com>)
#    Copyright (C) 2015-2017 Sergio Corato
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
    'name': 'Aeroo custom parser',
    'version': '8.0.1.0.1',
    'category': 'other',
    'author': 'Sergio Corato - Efatto.it, Didotech Srl',
    'website': 'http://www.efatto.it',
    'description': 'Aeroo custom parser function and fields.',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'report_aeroo',
        'stock',
        'l10n_it_ddt',
        'report_branding',
        'service_type',
    ],
    'data': [
        'views/invoice.xml',
        'views/company.xml',
        'views/report_invoice.xml',
    ],
    'installable': True
}
