# Copyright 2014 Didotech SRL (<http://www.didotech.com>).
# Copyright 2015-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Bank for riba and payment in partner",
    "version": "12.0.1.0.0",
    "category": "Localisation",
    "author": "Didotech SRL, SimplERP SRL, Sergio Corato",
    "website": "https://efatto.it",
    "description": "Add bank for riba and payment in partner and invoice",
    "license": "AGPL-3",
    "depends": [
        "account",
        "sale",
    ],
    "data": [
        "views/account_invoice_view.xml",
        "views/partner_view.xml",
        "views/sale_order_report.xml",
    ],
    "installable": True,
}
