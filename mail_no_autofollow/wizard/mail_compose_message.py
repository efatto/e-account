from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        for wizard in self:
            super(
                MailComposeMessage, wizard.with_context(mail_post_autofollow=False)
            ).send_mail(auto_commit=auto_commit)
