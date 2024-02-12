from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    email_shipping = fields.Char(string='Email Shipping')

    def action_do_send_email(self):
        """Opens a wizard to compose an email"""
        self.ensure_one()
        self.lang or self.env.context.get("lang")
        ctx = {
            "default_model": "res.partner",
            "default_res_id": self.ids[0],
            "default_composition_mode": "comment",
            "default_partner_ids": [self.id],
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }
