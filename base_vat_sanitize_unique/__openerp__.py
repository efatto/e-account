# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
    'name': 'Base VAT sanitize unique',
    'version': '8.0.1.1.1',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'description': 'Sanitize VAT number field for unique consistency',
    'website': 'http://www.efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'base_vat_sanitized',
        'l10n_it_fiscalcode',
    ],
    'data': [
    ],
    'installable': True,
}