# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _default_agents(self):
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents:
                vals = {
                    'agent': agent.id,
                    'commission': partner.default_sale_commission_id.id
                    or agent.commission.id,
                }
                vals['display_name'] = self.env['sale.order.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(default=_default_agents)


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
