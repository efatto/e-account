# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agents = fields.Many2many(
        comodel_name='res.partner',
        domain=[('agent', '=', True)]
    )

    @api.multi
    @api.depends('agent', 'order_line')
    def update_agents(self):
        for order in self:
            for line in order.order_line:
                agents = []
                for agent in order.agents:
                    vals = {
                        'agent': agent.id,
                        'commission': agent.commission.id,
                    }
                    vals['display_name'] = self.env[
                        'account.invoice.line.agent'] \
                        .new(vals).display_name
                    agents.append(vals)
                line.agents.unlink()
                if line.product_id.product_tmpl_id.service_type not in (
                        'transport', 'other', 'contribution'):
                    line.agents = [(0, 0, x) for x in agents]
