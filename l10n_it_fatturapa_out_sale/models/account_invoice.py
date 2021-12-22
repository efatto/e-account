# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    fatturapa_sale_order_data = fields.Boolean(
        related='partner_id.fatturapa_sale_order_data'
    )
