# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    bank_riba_id = fields.Many2one('res.bank', 'Bank for ri.ba.')
    company_bank_id = fields.Many2one(
        'res.partner.bank', string='Company bank for Bank Transfer')
