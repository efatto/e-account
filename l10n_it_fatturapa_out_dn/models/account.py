
from odoo import fields, models, api


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    carrier_id = fields.Many2one(
        'res.partner', string='Carrier')
