from odoo import api, models


class MailThreadCC(models.AbstractModel):
    _inherit = "mail.thread.cc"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        # remove recipient added in cc
        if self._context.get("mark_shipping_email_as_sent") and msg_dict.get("cc"):
            msg_dict.pop("cc")
        return super().message_new(msg_dict, custom_values=custom_values)

    def message_update(self, msg_dict, update_vals=None):
        # remove recipient added in cc
        if self._context.get("mark_shipping_email_as_sent") and msg_dict.get("cc"):
            msg_dict.pop("cc")
        if self._context.get("mark_shipping_email_as_sent") and update_vals.get(
            "email_cc"
        ):
            update_vals.pop("email_cc")
        return super().message_update(msg_dict, update_vals=update_vals)
