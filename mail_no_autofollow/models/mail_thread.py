from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model_create_multi
    def create(self, vals_list):
        # Set default to no subscribe
        return super(
            MailThread, self.with_context(mail_create_nosubscribe=True)
        ).create(vals_list=vals_list)

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        """Force to no autofollow as in many models (sale.order, purchase.order, ...) it
        is set to True by default.
        """
        mail_post_autofollow = False
        return super(
            MailThread, self.with_context(mail_post_autofollow=mail_post_autofollow)
        ).message_post(**kwargs)

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        # Remove auto-subscribe by default
        super()._message_auto_subscribe_followers(
            updated_values=updated_values, default_subtype_ids=default_subtype_ids
        )
        return []
