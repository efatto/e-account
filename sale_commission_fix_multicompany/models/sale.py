# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_agents(self):
        agents = []
        if self.env.context.get('partner_id'):
            partner = self.env['res.partner'].browse(
                self.env.context['partner_id'])
            for agent in partner.agents.filtered(
                lambda a: a.company_id == self.env.user.company_id
            ):
                vals = {
                    'agent': agent.id,
                    'commission': agent.commission.id,
                }
                vals['display_name'] = self.env['sale.order.line.agent']\
                    .new(vals).display_name
                agents.append(vals)
        return [(0, 0, x) for x in agents]

    agents = fields.One2many(default=_default_agents)