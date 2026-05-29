from odoo import api, fields, models
from odoo.fields import Command
from odoo.tools.safe_eval import safe_eval


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    notify_followers = fields.Boolean(default=False)

    @api.model
    def default_get(self, fields_list):
        # Add followers as email recipients as no more notified by default, to show
        # them to the user, who will remove them directly if needed
        res = super().default_get(fields_list=fields_list)

        if res.get("model") and res.get("res_ids"):
            follower_ids = (
                self.env[res["model"]]
                .browse(safe_eval(res["res_ids"]))
                .message_partner_ids
            )
            if follower_ids:
                partners = self.env["res.partner"]
                for follower_id in follower_ids:
                    user_id = (
                        self.env["res.users"]
                        .with_context(active_test=False)
                        .search([("partner_id", "=", follower_id.id)], limit=1)
                    )
                    if user_id.login == "__system__":
                        # exclude odoo bot
                        continue
                    if user_id == self.env.user:
                        # exclude sending user
                        continue
                    partners |= follower_id
                res["partner_ids"] = [Command.set(partners.ids)]
        return res
