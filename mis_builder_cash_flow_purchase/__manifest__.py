# Copyright 2022-2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MIS Builder purchase cash flow",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "Generate automatically cash flow lines from purchase order line.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "mis_builder_cash_flow_inheritable",
        "account_payment_purchase",
        "purchase",
    ],
    "data": [
        "views/purchase.xml",
        "views/cashflow_line.xml",
    ],
    "installable": True,
    "post_init_hook": "create_cashflow_lines",
}
