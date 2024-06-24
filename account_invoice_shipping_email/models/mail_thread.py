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

    def _notify_email_recipient_values(self, recipient_ids):
        res = super()._notify_email_recipient_values(recipient_ids=recipient_ids)
        if self.env.context.get("default_email_cc"):
            res.update(
                {
                    "email_cc": self.env.context[
                        "default_email_cc"
                    ],  # format email safely
                }
            )
        return res

    def _notify_thread(self, message, msg_vals=False, notify_by_email=True, **kwargs):
        if self.env.context.get("default_email_cc"):
            # remove recipient added in cc, to send only 1 mail
            partners = self.env["res.partner"].browse(msg_vals["partner_ids"])
            for partner in partners:
                if partner.email == self.env.context.get("default_email_cc"):
                    msg_vals["partner_ids"].remove(partner.id)
        res = super()._notify_thread(
            message=message,
            msg_vals=msg_vals,
            notify_by_email=notify_by_email,
            **kwargs
        )
        return res
