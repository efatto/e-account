from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        """
        Force reply_to as it is overriden by the catchall.
        Force email_cc as it is ignored.
        """
        if self.env.context.get("default_reply_to", False):
            kwargs["reply_to"] = self.env.context.get("default_reply_to")
        if self.env.context.get("default_email_cc", False):
            kwargs["email_cc"] = self.env.context.get("default_email_cc")
        return super().message_post(**kwargs)
