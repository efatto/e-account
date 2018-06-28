# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _, fields
from openerp.tools import config
from time import time
import base64
import openerp
import zipfile
import os


class AccountInvoiceAttachment(models.Model):
    _name = "account.invoice.attachment"
    _description = "Account Inv Export File"
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _inherit = ['mail.thread']

    ir_attachment_id = fields.Many2one(
            'ir.attachment', 'Attachment', required=True, ondelete="cascade")


class WizardAccountInvoiceExport(models.TransientModel):
    _name = "wizard.account.invoice.export"

    invoice_report = fields.Many2one('ir.actions.report.xml')
    export_report_name = fields.Char()
    data = fields.Binary("File", readonly=True)
    name = fields.Char('Filename', size=32, readonly=True)
    state = fields.Selection((
        ('create', 'create'),
        ('get', 'get'),
    ), default='create')

    @api.multi
    def export_report(self):
        report_name = False
        if self._context['active_model'] == 'account.invoice':
            report_name = 'account.report_invoice'
        if report_name:
            ir_actions_report = self.env['ir.actions.report.xml']
            report = ir_actions_report.search([
                ('report_name', '=', report_name)
            ], limit=1)
            attachment_ids = []
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
                        attachment_ids += [attachment_id]

            path = os.path.join(config['data_dir'], "filestore",
                                self.env.cr.dbname)
            compression = zipfile.ZIP_STORED
            zf = zipfile.ZipFile("RAWs.zip", mode="w")
            for attachment_id in attachment_ids:
                file_name = attachment_id.store_fname
                zf.write(os.path.join(path, file_name),
                         attachment_id.name.replace('/', '_'),
                         compress_type=compression)
            zf.close()
            data = open("RAWs.zip", 'rb').read()
            export_report_name = self.export_report_name or 'Zip export report'
            attach_vals = {
                'name': export_report_name + '.zip',
                'datas_fname': export_report_name + '.zip',
                'datas': base64.encodestring(data),
            }
            account_invoice_attachment_out_id = self.env[
                'account.invoice.attachment'].create(attach_vals)
            model_data_obj = self.env['ir.model.data']
            view_rec = model_data_obj.get_object_reference(
                'report_account_invoice_export_zip',
                'view_invoice_attachment_form')
            view_id = view_rec and view_rec[1] or False
            return {
                'view_type': 'form',
                'name': "Export Invoices",
                'view_id': [view_id],
                'res_id': account_invoice_attachment_out_id.id,
                'view_mode': 'form',
                'res_model': 'account.invoice.attachment',
                'type': 'ir.actions.act_window',
                'context': self._context,
            }
