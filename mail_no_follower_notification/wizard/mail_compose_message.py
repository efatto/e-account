# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    notify_followers = fields.Boolean(default=False)

    @api.model
    def get_record_data(self, values):
        # Add followers as email recipients as no more notified by default, to show
        # them to the user, whom will remove them directly if needed
        res = super().get_record_data(values)
        if values.get("res_id") and values.get("model"):
            follower_ids = (
                self.env[values.get("model")]
                .browse(values.get("res_id"))
                .message_partner_ids
            )
            for follower_id in follower_ids:
                user_id = (
                    self.env["res.users"]
                    .with_context(active_test=False)
                    .search([("partner_id", "=", follower_id.id)])
                )
                if user_id.login == "__system__":
                    # exclude odoo bot
                    continue
                if user_id == self.env.user:
                    # exclude sending user
                    continue
                if not res.get("partner_ids", False):
                    res["partner_ids"] = [(4, follower_id.id)]
                elif follower_id.id not in res["partner_ids"]:
                    res["partner_ids"] += [(4, follower_id.id)]
        return res
