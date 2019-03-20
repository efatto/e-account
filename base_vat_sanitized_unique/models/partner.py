# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, _, api, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat')
    @api.multi
    def vat_onchange(self):
        for p in self:
            if p.vat and not p.parent_id:
                duplicated_partner_ids = self.env['res.partner'].search([
                    ('sanitized_vat', '=', p.vat.upper().replace(' ', '')),
                    ('id', '!=', p.id),
                    ('parent_id', '=', False)])
                if duplicated_partner_ids:
                    raise exceptions.ValidationError(
                        _('This VAT is already registered with %s partners') %
                        duplicated_partner_ids.mapped('name'))
