# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    default_sale_commission_id = fields.Many2one(
        comodel_name="sale.commission",
        string="Default commission",
        readonly=True)

    @api.multi
    def onchange_partner_id(self, part):
        res = super(SaleOrder, self).onchange_partner_id(part)
        if part:
            partner_id = self.env['res.partner'].browse(part)
            res['value'].update({
                'default_sale_commission_id':
                    partner_id.default_sale_commission_id.id})
        return res


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%s: %s" % (record.agent.name, record.commission.name)
            res.append((record.id, name))
        return res

    @api.depends('agent', 'commission')
    def _compute_display_name(self):
        return super(SaleOrderLineAgent, self)._compute_display_name()
