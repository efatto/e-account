# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Mrp production reserve on PO Confirmed or stock',
    'version': '12.0.1.0.0',
    'category': 'Manufacture',
    'license': 'AGPL-3',
    'summary': """
    Add a purchase ordered qty when a PO is confirmed in production raw moves.
    Set reserved in related raw component production lines on stock available or
    incoming moves.
    """,
    'author': "Sergio Corato",
    'website': 'https://github.com/sergiocorato/e-account',
    'depends': [
        'purchase_mrp',
        'purchase_line_procurement_group',
        'purchase_order_approved',
    ],
    'data': [
        'views/mrp_production.xml',
    ],
    'installable': True,
}
