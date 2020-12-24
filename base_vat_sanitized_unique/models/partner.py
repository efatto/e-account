from odoo import models, _, api, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('sanitized_vat')
    @api.multi
    def _check_sanitized_vat(self):
        for partner in self:
            duplicated_partner_ids = self.env['res.partner']
            if partner.sanitized_vat and not partner.parent_id:
                possible_duplicated_partner_ids = self.env['res.partner'].search([
                    ('sanitized_vat', '=', partner.sanitized_vat),
                    ('id', '!=', partner.id),
                    ('parent_id', '=', False)])
                if possible_duplicated_partner_ids:
                    # check if exists multiple partner for the same company
                    for company_id in partner.company_ids:
                        duplicated_partner_ids |= \
                            possible_duplicated_partner_ids.filtered(
                                lambda x: company_id in x.company_ids)
                    if duplicated_partner_ids:
                        raise exceptions.ValidationError(
                            _('VAT for partner %s is already registered with %s '
                              'partners') % (
                                  partner.name,
                                  duplicated_partner_ids.mapped('name'))
                        )
