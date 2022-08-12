from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, *args, **kwargs):
        """Force to no autofollow as in many models (sale.order, purchase.order, ...) it
        is set to True by default.
        """
        return super(MailThread, self.with_context(mail_post_autofollow=False)
                     ).message_post(*args, **kwargs)
