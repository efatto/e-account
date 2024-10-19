# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Mrp production reserve on PO Confirmed',
    'version': '12.0.1.0.0',
    'category': 'Manufacture',
    'license': 'AGPL-3',
    'summary': """
    When a PO is confirmed, set reserved in related raw component production lines.
    """,
    'author': "Sergio Corato",
    'website': 'https://github.com/sergiocorato/e-account',
    'depends': [
        'purchase_mrp',
        'purchase_order_approved',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True,
}
