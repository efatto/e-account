# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sale_number_total = fields.Integer(
        compute='_compute_sale_amount_total', string="Number of Orders")

    @api.depends('order_ids')
    def _compute_sale_amount_total(self):
        super()._compute_sale_amount_total()
        for lead in self:
            lead.sale_number_total = len(lead.order_ids.ids) - lead.sale_number
