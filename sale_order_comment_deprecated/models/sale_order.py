# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    note1 = fields.Html('Top Comment')
    note2 = fields.Html('Bottom Comment')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    formatted_note = fields.Html('Formatted Note')
