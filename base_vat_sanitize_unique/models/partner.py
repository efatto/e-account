# -*- coding: utf-8 -*-

from openerp import models, _, api, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('sanitized_vat')
    @api.multi
    def _check_sanitized_vat(self):
        for partner in self:
            if partner.sanitized_vat and not partner.parent_id:
                domain = [
                    ('sanitized_vat', '=', partner.sanitized_vat),
                    ('id', '!=', partner.id),
                    ('parent_id', '=', False)]
                if self.fiscalcode:
                    domain.append(('fiscalcode', '=', self.fiscalcode))
                duplicated_partner_ids = self.env['res.partner'].search(domain)
                if duplicated_partner_ids:
                    raise exceptions.ValidationError(
                        _('This VAT is already registered with %s partners') %
                        duplicated_partner_ids.mapped('name'))
