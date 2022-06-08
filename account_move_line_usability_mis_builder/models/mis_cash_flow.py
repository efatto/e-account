from odoo import models, fields


class MisCashFlow(models.Model):
    _inherit = 'mis.cash_flow'

    name = fields.Text(
        readonly=True,
    )
