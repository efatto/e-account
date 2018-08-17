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
    'name': 'Default sales discount per partner not for other services',
    'version': '8.0.1.0.0',
    'category': 'Sale',
    'description': 'Discount will not applied to other services types',
    'license': 'AGPL-3',
    'author': 'Sergio Corato',
    'website': 'https://www.efatto.it',
    'depends': [
        'discount_complex',
        'partner_default_sale_discount',
        'product_category_nodiscount',
        'service_type',
    ],
    'data': [
    ],
    'installable': False,
}
