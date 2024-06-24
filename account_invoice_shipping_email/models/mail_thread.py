from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_by_email_add_values(self, base_mail_values):
        res = super()._notify_by_email_add_values(base_mail_values=base_mail_values)
        if self.env.context.get("default_email_cc"):
            emails_normalized = tools.email_normalize_all(
                self.env.context["default_email_cc"]
            )
            if emails_normalized:
                res.update(
                    {
                        "email_cc": ",".join(emails_normalized),
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
