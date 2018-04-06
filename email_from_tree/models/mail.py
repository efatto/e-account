# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _, fields
from time import time
import base64
import openerp


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def generate_email_for_composer_batch(
            self, template_id, res_ids, context=None, fields=None):
        values = super(MailComposeMessage, self
                       ).generate_email_for_composer_batch(
            template_id, res_ids, context=context, fields=fields
        )
        if self._context['active_model'] == 'account.invoice':
            report_name = 'account.report_invoice'
            template = 'email_template_invoice_from_tree'
        elif self._context['active_model'] == 'sale.order':
            report_name = 'sale.report_saleorder'
            template = 'email_template_sale_from_tree'
        else:
            report_name = False
            template = False
        if report_name and template:
            ir_actions_report = self.env['ir.actions.report.xml']
            report = ir_actions_report.search([
                ('report_name', '=', report_name)
            ], limit=1)
            template_id = self.env['ir.model.data'].get_object_reference(
                'email_from_tree', template
            )
        if not template_id:
            raise exceptions.ValidationError(_('No template found!'))
        attachment_ids = []
        if self._context.get('default_template_id', False) == template_id[1]:
            for obj in self.env[self._context['active_model']].browse(
                    self._context['active_ids']):
                attachment_obj = self.env['ir.attachment']
                if report:
                    (result, format) = openerp.report.render_report(
                        self._cr, self._uid, [obj.id],
                        report.report_name,
                        {'model': obj._name},
                        self._context)
                    eval_context = {'time': time,
                                    'object': obj}
                    if not report.attachment or not eval(
                            report.attachment, eval_context):
                        # no auto-saving of report as attachment,
                        # need to do it manually
                        result = base64.b64encode(result)
                        file_name = '%s_%s.pdf' % (
                            obj.partner_id.name,
                            obj.number if self._context['active_model'] ==
                            'account.invoice' else obj.name)
                        attachment_id = attachment_obj.create({
                                'name': file_name,
                                'datas': result,
                                'datas_fname': file_name,
                                'res_model': obj._name,
                                'res_id': obj.id,
                                'type': 'binary'
                            })
                        attachment_ids += [attachment_id.id]
            values[values.keys()[0]].update({'attachment_ids': attachment_ids})
        return values
