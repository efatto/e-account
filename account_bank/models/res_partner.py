# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_company_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Company bank for Bank Transfer',
        company_dependent=True,
        help='One of company bank for payment to be received by partner')
