# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MIS Builder sale cash flow",
    "version": "12.0.1.0.1",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Generate automatically cash flow lines from sale order line.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "mis_builder_cash_flow_inheritable",
        "account_payment_sale",
        "sale",
        "sale_order_deposit_percent",
        "sale_order_line_date",
    ],
    "data": [
        "views/sale.xml",
        "views/cashflow_line.xml",
    ],
    "installable": True,
    "post_init_hook": "create_cashflow_lines",
}
