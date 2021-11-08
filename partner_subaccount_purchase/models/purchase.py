# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        if not partner_id:
            return res
        partner = self.env['res.partner'].browse(partner_id)
        if partner.property_account_payable.type == 'view':
            partner.write({'supplier': True})
        return res
