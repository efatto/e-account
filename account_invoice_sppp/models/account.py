# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    stock_picking_package_preparation_ids = fields.One2many(
        'stock.picking.package.preparation', 'invoice_id', 'DDTs',
        groups="stock.group_stock_user", readonly=True)

    @api.multi
    def unlink(self):
        invoices = self.filtered(lambda x: x.state == 'draft')
        pickings = invoices.mapped('stock_picking_package_preparation_ids'
                                   ).filtered(
            lambda x: x.state != 'cancel')
        pickings.write({'invoice_state': '2binvoiced'})
        return super(AccountInvoice, self).unlink()

    @api.multi
    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        pickings = self.mapped('stock_picking_package_preparation_ids'
                               ).filtered(
            lambda x: x.state != 'cancel')
        pickings.write({'invoice_state': '2binvoiced'})
        return res

    @api.multi
    def action_cancel_draft(self):
        res = super(AccountInvoice, self).action_cancel_draft()
        pickings = self.mapped('stock_picking_package_preparation_ids'
                               ).filtered(
            lambda x: x.state != 'cancel')
        pickings.write({'invoice_state': 'invoiced'})
        return res
