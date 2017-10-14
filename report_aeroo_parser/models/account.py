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

    @api.multi
    def _get_amount_taxable_lines(self):
        for invoice in self:
            amount_taxable = amount_tax = 0.0
            for line in invoice.tax_line.filtered(
                lambda x: not (
                    x.tax_code_id.exclude_from_registries and
                    x.tax_code_id.notprintable and
                    x.tax_code_id.withholding_type
                )
            ):
                amount_taxable += line.base_amount
                amount_tax += line.amount
            invoice.base_amount_tax = amount_taxable
            invoice.tax_amount_tax = amount_tax
            invoice.total_amount_tax = amount_taxable + amount_tax

    base_amount_tax = fields.Float(compute=_get_amount_taxable_lines)
    tax_amount_tax = fields.Float(compute=_get_amount_taxable_lines)
    total_amount_tax = fields.Float(compute=_get_amount_taxable_lines)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    def _get_price_unit_net(self):
        for line in self:
            line.price_unit_net = line.price_unit * (
                1 - line.discount / 100.0)

    price_unit_net = fields.Float(compute=_get_price_unit_net)
