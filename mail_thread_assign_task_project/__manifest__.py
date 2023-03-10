# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Assign task created from mail message to project',
    'version': '12.0.1.0.2',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'If exists a project for a mail received with project.task '
                   'fallback model in email smtp server, it will be assigned to '
                   'this. '
                   'N.B.: This module is useful only if you have a single project for '
                   'customer!',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'LGPL-3',
    'depends': [
        'mail',
    ],
    'installable': True
}
