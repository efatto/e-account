
from odoo import api, fields, models
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_exportable_reduced_price = fields.Boolean(
        compute="_compute_is_exportable_reduced_price",
        store=True,
    )

    @api.depends(
        "invoice_line_ids.is_exportable_reduced_price",
    )
    def _compute_is_exportable_reduced_price(self):
        for invoice in self:
            if all(
                line.is_exportable_reduced_price for line in invoice.invoice_line_ids
            ):
                invoice.is_exportable_reduced_price = True
            else:
                invoice.is_exportable_reduced_price = False


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_reduced_tax_excluded = fields.Float(
        compute="_get_price_reduced_tax_excluded",
        digits=(16, 8),
        store=True,
    )
    is_exportable_reduced_price = fields.Boolean(
        compute="_compute_is_exportable_reduced_price",
        store=True,
    )

    @api.depends('price_subtotal', 'quantity', 'discount', 'discount2', 'discount3')
    def _get_price_reduced_tax_excluded(self):
        for line in self:
            if line.price_subtotal and line.quantity and (
                line.discount or line.discount2 or line.discount3
            ):
                line.price_reduced_tax_excluded = (
                    line.price_subtotal / line.quantity
                )
            else:
                line.price_reduced_tax_excluded = line.price_unit

    @api.depends("price_subtotal", "quantity", "discount", "discount2", "discount3")
    def _compute_is_exportable_reduced_price(self):
        for line in self:
            if line.price_subtotal and line.quantity and (
                line.discount or line.discount2 or line.discount3
            ):
                if float_compare(
                    line.quantity * line.price_reduced_tax_excluded,
                    line.price_subtotal,
                    precision_rounding=line.currency_id.rounding
                ) != 0:
                    line.is_exportable_reduced_price = False
                else:
                    line.is_exportable_reduced_price = True
            # reduced price is the same as unit price
            line.is_exportable_reduced_price = True
