from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    order_confirmation_ai_connection_id = fields.Many2one(
        comodel_name="ai.connection",
        string="Order confirmation AI connection",
        domain=[("active", "=", True)],
        config_parameter="order_confirmation_checker.ai_connection_id",
        help="AI connection used to read order confirmations and create the "
        "sale order lines from the attachment.",
    )
