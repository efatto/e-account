# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MIS Builder sale progress cash flow",
    "version": "12.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Generate automatically cash flow lines from sale order progress.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "mis_builder_cash_flow_sale",
        "sale_order_progress",
    ],
    "data": [
        "views/sale.xml",
        "views/cashflow_line.xml",
    ],
    "installable": True,
    "post_init_hook": "create_cashflow_lines",
}
