# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    margin_min = fields.Float(
        string="Minimum margin on order line",
        default=20.0,
        help="An order line with a margin below this value will be signaled in red."
    )
    margin_max = fields.Float(
        string="Maximum margin on order line",
        default=100.0,
        help="An order line with a margin over this value will be signaled in grey."
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    margin_min = fields.Float(
        related='company_id.margin_min',
        string="Minimum margin on order line",
        help="An order line with a margin below this value will be signaled in red.",
        readonly=False
    )
    margin_max = fields.Float(
        related='company_id.margin_max',
        string="Maximum margin on order line",
        help="An order line with a margin over this value will be signaled in grey.",
        readonly=False
    )
