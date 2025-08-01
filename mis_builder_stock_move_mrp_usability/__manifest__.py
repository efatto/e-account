# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Glue module from stock move + MRP + MIS - DEPRECATED',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Sergio Corato',
    'summary': 'Add fields from MRP Bom evalution in stock move and show in MIS Builder'
               ' report.',
    'website': 'https://github.com/efatto/e-account',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        "mis_builder_query_drilldown_view",
        "mrp_bom_evaluation",
    ],
    'data': [
        "views/stock.xml",
    ],
    'installable': True,
    'auto_install': False,
}
