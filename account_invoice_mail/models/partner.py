# -*- coding: utf-8 -*-

from openerp import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_email = fields.Char('Invoice Email')
