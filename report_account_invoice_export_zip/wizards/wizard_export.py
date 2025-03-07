
from odoo import fields, models
from odoo.tools import config
import base64
import zipfile
import os
import tempfile


class WizardAccountInvoiceExport(models.TransientModel):
    _name = "wizard.account.invoice.export"

    export_report_name = fields.Char()
    data = fields.Binary("File", readonly=True)
    name = fields.Char('Filename', size=32, readonly=True)

    def export_report(self):
        # ir_actions_report = self.env['ir.actions.report.xml']
        # report = ir_actions_report.search([
        #     ('report_name', '=', report_name)
        # ], limit=1)
        attachments = []
        attachment_obj = self.env['ir.attachment']
        for attach in self.env["fatturapa.attachment.in"].browse(
                self._context['active_ids']
        ):
            fatturapa_attachment_model = self.env["fatturapa.attachment"]
            html = fatturapa_attachment_model.get_fattura_elettronica_preview(attach)
            pdf = self.env["ir.actions.report"]._run_wkhtmltopdf([html])
            # if report and obj.type in ['out_invoice', 'out_refund']:
            #     (result, report_format) = openerp.report.render_report(
            #         self._cr, self._uid, [obj.id],
            #         report.report_name,
            #         {'model': obj._name},
            #         self._context)
            #     eval_context = {'time': time,
            #                     'object': obj}
            #     if not report.attachment or not eval(
            #             report.attachment, eval_context):
            #         # no auto-saving of report as attachment,
            #         # need to do it manually
            result = base64.b64encode(pdf)
            file_name = '%s_%s.pdf' % (
                attach.xml_supplier_id.name,
                attach.invoices_number
            )
            att = attachment_obj.create({
                'name': file_name,
                'datas': result,
                # 'store_fname': file_name,
                'res_model': attach._name,
                'res_id': attach.id,
                'type': 'binary'
            })
            attachments += [att]

        path = os.path.join(config['data_dir'], "filestore", self.env.cr.dbname)
        compression = zipfile.ZIP_STORED
        temp = tempfile.mktemp(suffix='.zip')
        zf = zipfile.ZipFile(temp, mode="w")
        for attachment in attachments:
            file_name = attachment.store_fname
            zf.write(os.path.join(path, file_name),
                     attachment.name.replace('/', '_'),
                     compress_type=compression)
        zf.close()
        data = open(temp, 'rb').read()
        export_report_name = self.export_report_name or 'Zip export report'



        attach_vals = {
            'name': export_report_name + '.zip',
            'datas_fname': export_report_name + '.zip',
            'datas': base64.encodebytes(data),
        }
        mail_template[0].with_context({
            'lang': 'it_IT',
        }).send_mail(late_picking.id)
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
