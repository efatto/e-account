# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    print_net_price = fields.Boolean()
    print_hide_uom = fields.Boolean()
    print_shipping_address = fields.Boolean()
