# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, _, api, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def vat_change(self, vat):
        if vat:
            duplicated_partner_ids = self.env['res.partner'].search([
                ('sanitized_vat', '=', vat.upper().replace(' ', '')),
                ('id', '!=', self.id),
                ('parent_id', '=', False),
            ])
            if duplicated_partner_ids:
                raise exceptions.ValidationError(
                    _('This VAT is already registered with %s partners') %
                    duplicated_partner_ids.mapped('name')
                )
        return super(ResPartner, self).vat_change(vat)
