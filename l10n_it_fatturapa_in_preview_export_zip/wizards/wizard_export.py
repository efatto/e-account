import base64
import os
import tempfile
import zipfile

from odoo import fields, models
from odoo.tools import config


class WizardAccountInvoiceExport(models.TransientModel):
    _name = "wizard.account.invoice.export"

    export_report_name = fields.Char(string="Exported file name")
    data = fields.Binary("File", readonly=True)
    name = fields.Char("Filename", readonly=True)

    def export_report(self):
        attachment_obj = self.env["ir.attachment"]
        attachments = attachment_obj.browse()
        for attach in self.env["fatturapa.attachment.in"].browse(
            self._context["active_ids"]
        ):
            fatturapa_attachment_model = self.env["fatturapa.attachment"]
            html = fatturapa_attachment_model.get_fattura_elettronica_preview(attach)
            pdf = self.env["ir.actions.report"]._run_wkhtmltopdf([html])
            result = base64.b64encode(pdf)
            file_name = "%s_%s.pdf" % (
                attach.xml_supplier_id.name,
                attach.invoices_number,
            )
            att = attachment_obj.create(
                {
                    "name": file_name,
                    "datas": result,
                    "res_model": attach._name,
                    "res_id": attach.id,
                    "type": "binary",
                }
            )
            attachments |= att

        path = os.path.join(config["data_dir"], "filestore", self.env.cr.dbname)
        compression = zipfile.ZIP_STORED
        temp = tempfile.mktemp(suffix=".zip")
        zf = zipfile.ZipFile(temp, mode="w")
        for attachment in attachments:
            file_name = attachment.store_fname
            zf.write(
                os.path.join(path, file_name),
                attachment.name.replace("/", "_"),
                compress_type=compression,
            )
        zf.close()
        data = open(temp, "rb").read()
        export_report_name = self.export_report_name or "Zip export report"
        zip_att = attachment_obj.create(
            {
                "name": export_report_name + ".zip",
                "datas": base64.encodebytes(data),
                "type": "binary",
            }
        )
        return {
            "view_type": "form",
            "name": "Export Invoices",
            "res_id": zip_att.id,
            "view_mode": "form",
            "res_model": "ir.attachment",
            "type": "ir.actions.act_window",
            "context": self._context,
        }
