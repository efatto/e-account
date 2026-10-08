# Copyright 2025 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Check Sale/Purchase Order Confirmation",
    "version": "18.0.1.0.0",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "category": "other",
    "depends": [
        "product_customerinfo",
        "purchase_stock",
        "sale_stock",
    ],
    "summary": "Add a check method for document received from customer/vendor to "
    "confirm sale or purchase order",
    "data": [
        "views/purchase.xml",
        "views/sale.xml",
    ],
    "external_dependencies": {"python": ["pytesseract"]},
    "installable": True,
}
