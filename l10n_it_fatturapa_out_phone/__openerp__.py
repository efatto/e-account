# -*- coding: utf-8 -*-
# Copyright 2014 Davide Corio
# Copyright 2015-2016 Lorenzo Battistini - Agile Business Group
# Copyright 2018 Gianmarco Conte, Marco Calcagni - Dinamiche Aziendali srl
# Copyright 2018 Sergio Corato
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Italian Localization - Fattura elettronica fix telefono',
    'version': '8.0.1.0.0',
    'category': 'Localization/Italy',
    'summary': 'Emissione fatture elettroniche fix telefono',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'LGPL-3',
    "depends": [
        'l10n_it_fatturapa_out',
        ],
    "data": [
    ],
    'installable': True,
    'external_dependencies': {
        'python': ['unidecode'],
    }
}
