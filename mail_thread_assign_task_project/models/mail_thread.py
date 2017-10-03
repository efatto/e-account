# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, api, _, models, tools


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route_process(self, message, message_dict, routes):
        res = super(MailThread, self).message_route_process(
            message, message_dict, routes
        )
        # get from message mail_from
        # check if is of a partner
        # check if exist a project with this partner
        # assign the task (if is a task) to this project
        for model, thread_id, custom_values, user_id, alias in routes or ():
            if model == 'project.task':
                email_from = message_dict.get('from')
                email = tools.email_split(email_from)
                partner = self.env['res.partner'].search(
                    [('email', '=', email[0])], limit=1)
                if partner:
                    commercial_partner = partner.commercial_partner_id
                    if commercial_partner:
                        project_id = self.env['project.project'].search([
                            ('partner_id', '=', commercial_partner.id)
                        ], limit=1)
                        if project_id:
                            self.env[model].browse(res).write({
                                'project_id': project_id.id,
                            })
        return res
