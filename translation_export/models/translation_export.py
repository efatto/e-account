import base64

from odoo import fields, models


class TranslationExport(models.Model):
    _name = "translation.export"
    _inherit = "mail.thread"
    _description = "Translation Export"

    name = fields.Char(string="Name", required=True)
    max_export_number = fields.Integer(
        string="Max number of exports",
        default=3,
    )

    def button_create_export(self):
        self.create_export()

    def cron_create_export(self):
        self.search([]).create_export()

    def create_export(self):
        report = self.env.ref("translation_export.xlsx_translation_export")
        attachment_obj = self.env["ir.attachment"]
        for rec in self:
            existing_attachments = attachment_obj.search([
                ("res_model", "=", rec._name),
                ("res_id", "=", rec.id),
            ], order="id desc")
            if len(existing_attachments) > rec.max_export_number:
                existing_attachments[:-rec.max_export_number].unlink()
            report_content, report_type = report._render_xlsx(rec.ids, [])
            result = base64.b64encode(report_content)
            file_name = "%s_%s.xlsx" % (
                rec.name,
                fields.Date.context_today(rec).strftime("%d_%m_%Y"),
            )
            attachment_obj.create(
                {
                    "name": file_name,
                    "datas": result,
                    "res_model": rec._name,
                    "res_id": rec.id,
                    "type": "binary",
                }
            )
