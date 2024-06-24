from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        """Force reply_to as it is overriden by the catchall."""
        if self.env.context.get("default_reply_to", False):
            kwargs["reply_to"] = self.env.context.get("default_reply_to")
        return super().message_post(**kwargs)
