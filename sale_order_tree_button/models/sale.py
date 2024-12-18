from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_view_opportunity(self):
        action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_opportunities')
        if self.partner_id.is_company:
            action['domain'] = [('partner_id.commercial_partner_id.id', '=', self.partner_id.id)]
        else:
            action['domain'] = [('partner_id.id', '=', self.partner_id.id)]
        return action
