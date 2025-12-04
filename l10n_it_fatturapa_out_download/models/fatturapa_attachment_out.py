import base64

from odoo import models


class FatturapaAttachmentOut(models.Model):
    _inherit = "fatturapa.attachment.out"

    def get_url_report(self):
        self.ensure_one()
        attachment_obj = self.env["ir.attachment"]
        html = self.env["fatturapa.attachment"].get_fattura_elettronica_preview(self)
        pdf = self.env["ir.actions.report"]._run_wkhtmltopdf([html])
        result = base64.b64encode(pdf)
        file_name = "%s_%s.pdf" % (
            self.invoice_partner_id.name,
            self.out_invoice_ids[0].name.replace("/", "_"),
        )
        att = attachment_obj.create(
            {
                "name": file_name,
                "datas": result,
                "res_model": self._name,
                "res_id": self.id,
                "type": "binary",
            }
        )
        att.generate_access_token()
        url = "{}/web/content/ir.attachment/{}/datas/{}?download=true{}".format(
            self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
            att.id,
            att.name,
            f"&access_token={att.access_token}",
        )
        return url
