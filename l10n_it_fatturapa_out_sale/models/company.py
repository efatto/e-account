# Copyright 2019-2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    fatturapa_out_sale_internal_ref = fields.Boolean(
        string="Internal sale order reference",
        help="Put in e-invoice reference to internal order, instead of "
             "reference of customer.")
    fatturapa_sale_order_data = fields.Boolean(
        string='Include sale order data in e-invoice')


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fatturapa_out_sale_internal_ref = fields.Boolean(
        related='company_id.fatturapa_out_sale_internal_ref',
        string="Internal sale order reference",
        help="Put in e-invoice reference to internal order, instead of "
             "reference of customer.",
        readonly=False)
    fatturapa_sale_order_data = fields.Boolean(
        related='company_id.fatturapa_sale_order_data',
        string='Include sale order data in e-invoice',
        readonly=False)
