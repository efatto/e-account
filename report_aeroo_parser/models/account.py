# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    stock_picking_package_preparation_ids = fields.One2many(
        'stock.picking.package.preparation', 'invoice_id', 'Pickings')
    tax_stamp_image = fields.Binary('Tax stamp')
    print_net_price = fields.Boolean()
    print_hide_uom = fields.Boolean()
    print_shipping_address = fields.Boolean()
    print_totals_in_first_page = fields.Boolean()
    print_payment_in_footer = fields.Boolean()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _get_price_unit_net(self):
        for line in self:
            line.price_unit_net = line.price_unit * (
                1 - line.discount / 100.0)

    price_unit_net = fields.Float(compute=_get_price_unit_net)
