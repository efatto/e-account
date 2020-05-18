from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    company_bank_id = fields.Many2one(
        'res.partner.bank', string='Company bank for Bank Transfer',
        help='One of my company bank for payment to be received by partner')
