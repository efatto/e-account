# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields, exceptions, _
import time


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery Method",
        help="Complete this field to add delivery cost to invoice.")

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False, payment_term=False,
            partner_bank_id=False, company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id:
            dtype = self.env['res.partner'].browse(
                partner_id).property_delivery_carrier.id
            # TDE NOTE: not sure the aded 'if dtype' is valid
            if dtype:
                res['value']['carrier_id'] = dtype
        return res

    @api.multi
    def _delivery_unset(self):
        for invoice in self:
            invoice.invoice_line.filtered(
                lambda x: x.is_delivery).unlink()

    @api.multi
    def delivery_set(self):
        line_obj = self.env['account.invoice.line']
        self._delivery_unset()
        line_ids = []
        for invoice in self:
            grid_id = invoice.carrier_id.grid_get(invoice.address_shipping_id.id)
            if not grid_id:
                raise exceptions.ValidationError(
                    _('No grid matching for this carrier!'))
            else:
                grid = self.env['delivery.grid'].browse(grid_id)
            if invoice.state not in ('draft', 'sent'):
                raise exceptions.ValidationError(
                    _('The invoice state have to be draft to add delivery '
                      'lines.'))

            taxes = grid.carrier_id.product_id.taxes_id.filtered(
                lambda t: t.company_id.id == invoice.company_id.id)
            taxes_ids = invoice.fiscal_position.map_tax(taxes) if \
                invoice.fiscal_position else False
            price_unit = grid.get_price_invoice(
                invoice, time.strftime('%Y-%m-%d'))
            # if invoice.company_id.currency_id.id != \
            #         invoice.pricelist_id.currency_id.id:
            #     price_unit = invoice.company_id.currency_id.with_context(
            #         date=invoice.date_invoice).\
            #         compute(invoice.pricelist_id.currency_id.id,
            #                 price_unit)
            values = {
                'invoice_id': invoice.id,
                'name': grid.carrier_id.name,
                'quantity': 1,
                'uos_id': grid.carrier_id.product_id.uom_id.id,
                'product_id': grid.carrier_id.product_id.id,
                'price_unit': price_unit,
                'tax_id': [(6, 0, taxes_ids)],
                'is_delivery': True,
            }
            res = line_obj.product_id_change(
                values['product_id'],
                values['uos_id'],
                partner_id=invoice.partner_id.id,
                qty=values['quantity'],
                )
            if res['value'].get('purchase_price'):
                values['purchase_price'] = res['value'].get('purchase_price')
            if invoice.invoice_line:
                values['sequence'] = invoice.invoice_line[-1].sequence + 1
            line_id = line_obj.create(values)
            line_ids.append(line_id)
        return line_ids


class DeliveryGrid(models.Model):
    _inherit = "delivery.grid"

    @api.multi
    def get_price_invoice(self, invoice, dt):
        for grid in self:
            total = weight = volume = quantity = 0
            for line in invoice.invoice_line:
                if not line.product_id.is_contribution\
                        and not line.product_id.is_other\
                        and not line.product_id.is_transport:
                    total += line.price_subtotal
                if not line.product_id or line.is_delivery:
                    continue
                q = line.uos_id._compute_qty(
                    line.quantity, line.product_id.uom_id.id)
                weight += (line.product_id.weight or 0.0) * q
                volume += (line.product_id.volume or 0.0) * q
                quantity += q
            total = invoice.currency_id.with_context(
                date=invoice.date_invoice
            ).compute(from_amount=total, to_currency=invoice.currency_id)
            return grid.get_price_from_invoice(
                total, weight, volume, quantity)

    @api.multi
    def get_price_from_invoice(self, total, weight, volume, quantity):
        for grid in self:
            price = 0.0
            ok = False
            price_dict = {'price': total, 'volume': volume, 'weight': weight,
                          'wv': volume*weight, 'quantity': quantity}
            for line in grid.line_ids:
                test = eval(
                    line.type+line.operator+str(line.max_value), price_dict)
                if test:
                    if line.price_type == 'variable':
                        price = line.list_price * price_dict[
                            line.variable_factor]
                    else:
                        price = line.list_price
                    ok = True
                    break
            if not ok:
                raise exceptions.ValidationError(
                    _("Selected product in the delivery method doesn't fulfill"
                      " any of the delivery grid(s) criteria."))
        return price
