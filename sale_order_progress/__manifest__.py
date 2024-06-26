# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order progress',
    'version': '12.0.1.0.0',
    'category': 'other',
    'author': 'Sergio Corato',
    'description': 'This module add the ability to link sale advance lines generated '
                   'in the invoices to sale progress, to compute amount to be invoiced '
                   'in specific dates of the sale order.',
    'website': 'https://github.com/sergiocorato/e-account',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/invoice.xml',
        'views/sale_order.xml',
        'views/sale_order_progress.xml',
        'views/sale_advance.xml',
    ],
    'installable': True,
}
