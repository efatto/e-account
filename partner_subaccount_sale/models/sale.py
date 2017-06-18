# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(SaleOrder, self).onchange_partner_id(partner_id)
        if not partner_id:
            return res
        partner = self.env['res.partner'].browse(partner_id)
        if partner.property_account_receivable.type == 'view':
            partner.write({'customer': True})
        return res
