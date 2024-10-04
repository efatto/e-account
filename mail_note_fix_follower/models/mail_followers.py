from odoo import models


class MailFollowers(models.Model):
    _inherit = "mail.followers"

    def _get_recipient_data(
        self, records, message_type, subtype_id, pids=None, cids=None
    ):
        if subtype_id == self.env.ref("mail.mt_note").id and pids:
            # notify notes only to partners with user
            partner_ids = self.env["res.partner"].browse(pids)
            pids = {partner.id for partner in partner_ids if partner.user_id}
        res = super()._get_recipient_data(records, message_type, subtype_id, pids, cids)
        return res


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_compute_recipients(self, message, msg_vals):
        if (
            msg_vals.get("subtype_id", False) == self.env.ref("mail.mt_note").id
            and not msg_vals.get("message_type") == "notification"
            and msg_vals.get("partner_ids", False)
        ):
            # notify notes only to partners with user
            partner_ids = self.env["res.partner"].browse(msg_vals["partner_ids"])
            pids = {partner.id for partner in partner_ids if partner.user_id}
            msg_vals["partner_ids"] = pids
            message.sudo().partner_ids = partner_ids
        return super()._notify_compute_recipients(message, msg_vals)
