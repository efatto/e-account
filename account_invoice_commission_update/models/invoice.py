# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    agents = fields.Many2many(
        comodel_name='res.partner',
        domain=[('agent', '=', True)],
        string='Update agents'
    )

    @api.multi
    @api.depends('agent', 'invoice_line')
    def invoice_update_agents(self):
        for inv in self:
            for line in inv.invoice_line:
                agents = []
                for agent in inv.agents:
                    commission_id = agent.commission
                    if inv.partner_id.default_sale_commission_id:
                        commission_id = inv.partner_id.\
                            default_sale_commission_id
                    vals = {
                        'agent': agent.id,
                        'commission': commission_id.id,
                    }
                    vals['display_name'] = self.env[
                        'account.invoice.line.agent'] \
                        .new(vals).display_name
                    agents.append(vals)
                line.agents.unlink()
                if line.product_id and not line.product_id.commission_free:
                    line.agents = [(0, 0, x) for x in agents]
