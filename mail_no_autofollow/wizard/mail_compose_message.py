from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        result_mails_su, result_messages = (
            self.env["mail.mail"].sudo(),
            self.env["mail.message"],
        )
        for wizard in self:
            result_mails_su_wizard, result_messages_wizard = super(
                MailComposeMessage, wizard.with_context(mail_post_autofollow=False)
            )._action_send_mail(auto_commit=auto_commit)
            result_mails_su |= result_mails_su_wizard
            result_messages |= result_messages_wizard
        return result_mails_su, result_messages
