# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Send shipping mail from invoice",
    "version": "14.0.1.0.1",
    "category": "Invoice Management",
    "license": "AGPL-3",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "depends": [
        "account_invoice_shipping_info",
        "res_partner_email_shipping",
    ],
    "data": [
        "views/invoice_view.xml",
    ],
    "installable": True,
}
