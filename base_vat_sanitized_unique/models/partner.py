from odoo import models, _, api, exceptions


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
                company_ids = partner.company_id
                if hasattr(partner, 'company_ids'):
                    # multicompany: if partner have company_ids, check for every company
                    # that there are no other partner with same VAT in the same company
                    company_ids = partner.company_ids
                if hasattr(partner, 'fiscalcode'):
                    # check for fiscalcode if exists
                    domain.extend([('fiscalcode', '=', partner.fiscalcode)])
                if company_ids:
                    for company in company_ids:
                        domain.extend([('company_id', '=', company.id)])
                        duplicated_partner_ids = self.env['res.partner'].search(domain)
                        if duplicated_partner_ids:
                            raise exceptions.ValidationError(
                                _('VAT for partner %s [%s] is already registered in'
                                  ' %s [%s] partners in company %s')
                                % (partner.name, partner.id,
                                   duplicated_partner_ids.mapped('name'),
                                   duplicated_partner_ids.ids,
                                   company.name)
                            )
                else:
                    duplicated_partner_ids = self.env['res.partner'].search(domain)
                    if duplicated_partner_ids:
                        raise exceptions.ValidationError(
                            _('VAT for partner %s [%s] is already registered in'
                              ' %s [%s] partners')
                            % (partner.name, partner.id,
                               duplicated_partner_ids.mapped('name'),
                               duplicated_partner_ids.ids)
                        )
