
from odoo import api, fields, models
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    export_invoice_reduced_price = fields.Boolean(
        related="partner_id.export_invoice_reduced_price",
        readonly=False,
    )


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
                    # diff_amount = (
                    #     line.price_subtotal
                    #     - float_round(
                    #         line.quantity * line.price_reduced_tax_excluded,
                    #         precision_rounding=line.currency_id.rounding
                    #     )
                    # )
                    line.is_exportable_reduced_price = False
                    # raise ValidationError(_(
                    #     "This invoice cannot be exported with reduced price option as "
                    #     "there is a residual total amount difference %0.2f in line %s")
                    #                       % (diff_amount, line.name)
                    #                       )
                else:
                    line.is_exportable_reduced_price = True
            # reduced price is the same as unit price
            line.is_exportable_reduced_price = True
