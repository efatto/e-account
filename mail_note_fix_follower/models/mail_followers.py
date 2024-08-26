from odoo import models


class MailFollowers(models.Model):
    _inherit = "mail.followers"

    def _get_recipient_data(
        self, records, message_type, subtype_id, pids=None, cids=None
    ):
        if subtype_id == self.env.ref("mail.mt_note").id:
            pids = set()
        res = super()._get_recipient_data(records, message_type, subtype_id, pids, cids)
        if subtype_id == self.env.ref("mail.mt_note").id:
            # FIXME remove partners if they are followers not set in @ only!!!
            #  set on purpose on the note!!!
            res = []
        return res


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_compute_recipients(self, message, msg_vals):
        if (
            msg_vals.get("subtype_id", False) == self.env.ref("mail.mt_note").id
            and not msg_vals.get("message_type") == "notification"
        ):
            msg_vals["partner_ids"] = set()
            message.sudo().partner_ids = False
        return super()._notify_compute_recipients(message, msg_vals)
