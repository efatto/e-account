# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    type = fields.Selection(
        selection=[('purchase', 'Purchase'), ('sale', 'Sale'),
                   ('all', 'All')],
        copy=False
    )

    @api.model
    def get_fiscal_position(self, company_id, partner_id, delivery_id=None):
        res = super(AccountFiscalPosition, self).get_fiscal_position(
            company_id=company_id, partner_id=partner_id,
            delivery_id=delivery_id)
        # todo if it is a sale, search type sale, else purchase
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(partner_id)
        model_type = self._context.get('type', False)
        # if no delivery use invocing #TODO is real case? a triangolation to EU
        # TODO delivered extra-EU is invoiced as extra-EU?
        if delivery_id:
            delivery = partner_obj.browse(delivery_id)
        else:
            delivery = partner

        # partner manually set fiscal position always win
        if delivery.property_account_position or \
                partner.property_account_position:
            return res

        #else search

        domains = [[('auto_apply', '=', True),
                    ('vat_required', '=', partner.vat_subjected),
                    ('company_id', '=', company_id)]]
        if partner.vat_subjected:
            # Possibly allow fallback to non-VAT positions,
            # if no VAT-required position matches
            domains += [[('auto_apply', '=', True),
                         ('vat_required', '=', False),
                         ('company_id', '=', company_id)]]

        for domain in domains:
            if delivery.country_id.id:
                fiscal_position_ids = self.search(
                    domain + [('type', '=', model_type),
                              ('country_id', '=', delivery.country_id.id)],
                    limit=1)
                if fiscal_position_ids:
                    return fiscal_position_ids.id
                # if do not exists specific type, search all type for country
                fiscal_position_ids = self.search(
                    domain + [('type', '=', 'all'),
                              ('country_id', '=', delivery.country_id.id)],
                    limit=1)
                if fiscal_position_ids:
                    return fiscal_position_ids.id
                # then search for specific type for group of countries
                fiscal_position_ids = self.search(
                    domain + [('type', '=', model_type),
                              ('country_group_id.country_ids', '=',
                               delivery.country_id.id)], limit=1)
                if fiscal_position_ids:
                    return fiscal_position_ids.id
                # finally search for all type for all countries
                fiscal_position_ids = self.search(
                    domain + [('type', '=', 'all'),
                              ('country_group_id.country_ids', '=',
                               delivery.country_id.id)], limit=1)
                if fiscal_position_ids:
                    return fiscal_position_ids.id

            fiscal_position_ids = self.search(
                domain + [('country_id', '=', None),
                          ('country_group_id', '=', None)], limit=1)
            if fiscal_position_ids:
                return fiscal_position_ids.id
        return False


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.cr_uid_ids_context
    def onchange_delivery_id(self, cr, uid, ids, company_id, partner_id,
                             delivery_id, fiscal_position, context=None):
        if context is None:
            context = {}
        context_sale = context.copy()
        context_sale.update({'type': 'sale'})
        return super(SaleOrder, self).onchange_delivery_id(
            cr, uid, ids, company_id=company_id, partner_id=partner_id,
            delivery_id=delivery_id, fiscal_position=fiscal_position,
            context=context_sale
        )

#TODO add purchase, invoice, etc.
