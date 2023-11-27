# Copyright 2023 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _default_volume_uom(self):
        return self.env["stock.delivery.note"]._default_volume_uom()

    def _domain_volume_uom(self):
        return self.env["stock.delivery.note"]._domain_volume_uom()

    def _default_weight_uom(self):
        return self.env["stock.delivery.note"]._default_weight_uom()

    def _domain_weight_uom(self):
        return self.env["stock.delivery.note"]._domain_weight_uom()

    gross_weight = fields.Float(string="Gross Weight")
    gross_weight_uom_id = fields.Many2one(
        'uom.uom', 'Gross Weight UoM',
        default=_default_weight_uom,
        domain=_domain_weight_uom,
    )
    net_weight = fields.Float(string="Weight")
    net_weight_uom_id = fields.Many2one(
        'uom.uom', 'Net Weight UoM',
        default=_default_weight_uom,
        domain=_domain_weight_uom,
    )
    volume = fields.Float('Volume')
    volume_uom_id = fields.Many2one(
        'uom.uom', 'Volume UoM',
        default=_default_volume_uom,
        domain=_domain_volume_uom,
    )
    transport_condition_id = fields.Many2one(
        "stock.picking.transport.condition",  # era 'stock.picking.carriage_condition'
        string='Carriage Condition')
    goods_appearance_id = fields.Many2one(
        "stock.picking.goods.appearance",  # era 'stock.picking.goods_description'
        string="Appearance of goods",)
    transport_reason_id = fields.Many2one(
        "stock.picking.transport.reason",  # era 'stock.picking.transportation_reason'
        string='Reason of transport')
    transport_method_id = fields.Many2one(
        "stock.picking.transport.method",  # era 'stock.picking.transportation_method'
        string='Method of transport')
    transport_datetime = fields.Datetime(
        string="Transport date"
    )
    carrier_id = fields.Many2one(
        'res.partner', string='Carrier')
    carrier_tracking_ref = fields.Char(string='Tracking Reference', copy=False)
    dimension = fields.Char()
    packages = fields.Integer('Packages')
