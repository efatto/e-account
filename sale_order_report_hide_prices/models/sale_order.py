# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    print_hide_prices = fields.Boolean(
        string='Hide prices in report?')
    print_hide_product_code = fields.Boolean(
        string='Hide product code in report?')
