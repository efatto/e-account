# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ddt_supplier_number = fields.Char(string='Supplier TD Number', copy=False)
    ddt_supplier_date = fields.Date(string='Supplier TD Date', copy=False)
