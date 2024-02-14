
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_open_export_send_sdi(self):
        res = super().action_open_export_send_sdi()
        if self.fatturapa_attachment_out_id.state == "sent":
            self.send_shipping_email()
        return res

    def send_shipping_email(self):
        self.ensure_one()
        lang = self.partner_id.lang or self.env.context.get("lang")
        template = self.env.ref(
            "account.email_template_edi_invoice"
        ).with_context(lang=lang)
        # possible other implementation, but without email status notification
        # res = template.send_mail(
        #     self.id,
        #     force_send=False,
        #     notif_layout="mail.mail_notification_light",
        # )
        # return res
        email_values = template.generate_email(
            self.ids, ["body_html", "subject", "reply_to", "email_to"])
        kwargs = {"mail_auto_delete": False}
        if email_values.get("reply_to", False):
            kwargs["reply_to"] = email_values["reply_to"]
        if email_values.get("email_to", False):
            kwargs["email_to"] = email_values["email_to"]
        values = email_values[self.id]
        self.message_post(
            author_id=self.env.user.partner_id.id,
            body=values["body_html"],
            message_type="email",
            subject=values["subject"],
            attachments=values["attachments"],
            email_from=template.email_from,
            subtype_xmlid='mail.mt_comment',
            **kwargs,
        )
        return True
