from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    shipping_email_state = fields.Selection(
        selection=[
            ("no", "Not sent"),
            ("sent", "Waiting confirm"),
            ("confirmed", "Shipping confirmed"),
        ],
        string="Shipping State",
        default="no",
    )

    def action_send_shipping_email(self):
        self.ensure_one()
        self.partner_id.lang or self.env.context.get("lang")
        template = self.partner_id.email_shipping_template_id
        ctx = {
            "default_model": "account.move",
            "default_res_id": self.id,
            "default_composition_mode": "comment",
            "default_use_template": bool(template),
            "default_template_id": template and template.id or False,
            "force_email": True,
            "mark_shipping_email_as_sent": True,
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

    def action_set_shipping_confirmed(self):
        self.ensure_one()
        self.shipping_email_state = "confirmed"
