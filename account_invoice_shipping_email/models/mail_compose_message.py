from odoo import fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        if (
            self._context.get("mark_shipping_email_as_sent", False)
            and self._context.get("default_model", False) == "account.move"
            and self._context.get("default_res_id", False)
        ):
            self.env["account.move"].browse(self._context["default_res_id"]).write(
                {
                    "shipping_email_state": "sent",
                    "shipping_email_date": fields.Datetime.now(),
                }
            )
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)
