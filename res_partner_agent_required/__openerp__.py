# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2017-2018 Sergio Corato
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
    'name': 'Agent required in partner and sale order creation',
    'version': '8.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'When creating a partner directly from a sale order, '
                   'agent is required with this module. '
                   'Partner cannot be created quickly - e.g. only with name.',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'res_partner_phone_email_required',
        'sale_commission',
    ],
    'data': [
        'views/partner.xml',
    ],
    'installable': False
}
