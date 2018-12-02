# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    @api.depends('tax_id', 'defaults')
    def copy(self):
        raise Warning(_("Tax can't be duplicated"))

    @api.model
    def create(self, vals):
        vat_account = False
        tax_code_obj = self.env['account.tax.code']
        company_id = self.env.user.company_id.id
        if vals.get('company_id', False):
            company_id = vals['company_id']
        if self.search([('name', '=', vals['name']),
                        ('company_id', '=', company_id)]):
            raise Warning(_("Tax name must be unique."))
        if vals.get('description', False):
            if self.search([('description', '=', vals['description']),
                            ('company_id', '=', company_id)]):
                raise Warning(_("Tax description must be unique."))
        if vals['type_tax_use'] == 'sale':
            vals.update({'base_sign': 1, 'tax_sign': 1,
                         'ref_base_sign': -1, 'ref_tax_sign': -1})
        elif vals['type_tax_use'] == 'purchase':
            vals.update({'base_sign': -1, 'tax_sign': -1,
                         'ref_base_sign': 1, 'ref_tax_sign': 1})

        if vals.get('base_code_id', False) and vals.get('tax_code_id', False):
            return super(AccountTax, self).create(vals)

        if not vals.get('base_code_id', False) and \
                vals.get('account_base_tax_code_id'):
            parent_base_tax_code = tax_code_obj.browse(
                vals['account_base_tax_code_id'])
            base_tax_code_vals = {
                'name': vals['name'] + ' (imp)',
                'code': parent_base_tax_code.code + vals['description'],
                'parent_id': vals['account_base_tax_code_id'],
                'is_base': True,
                'company_id': company_id,
                'vat_statement_type':
                vals['type_tax_use'] == 'sale' and 'debit' or
                vals['type_tax_use'] == 'purchase' and 'credit',
                'vat_statement_sign':
                vals['type_tax_use'] == 'sale' and 1 or
                vals['type_tax_use'] == 'purchase' and -1,
            }
            i = 0
            name = vals['name'] + ' (imp)'
            while True:
                if tax_code_obj.search([('name', '=', name),
                                        ('company_id', '=', company_id)]):
                    name += str(i)
                    i += 1
                else:
                    if i > 0:
                        base_tax_code_vals['name'] += str(i)
                    break
            base_code = tax_code_obj.create(base_tax_code_vals)
            vat_account = base_code.vat_statement_account_id if \
                base_code.vat_statement_account_id else \
                base_code.parent_id.vat_statement_account_id if \
                base_code.parent_id and base_code.parent_id. \
                vat_statement_account_id else False
            vals.update({'base_code_id': base_code.id,
                         'ref_base_code_id': base_code.id})
        if not vals.get('account_tax_code_id', False) and not \
                vals.get('tax_code_id', False) and vat_account:
            # is a tax without amount - exempt or similar
            vals.update({'account_collected_id': vat_account.id if
                         vat_account else False,
                         'account_paid_id': vat_account.id if
                         vat_account else False,
                         })

        if not vals.get('tax_code_id', False) and vals.get(
                'account_tax_code_id', False):
            parent_tax_code = tax_code_obj.browse(vals['account_tax_code_id'])
            tax_code_vals = {
                'name': vals['name'],
                'code': parent_tax_code.code + vals['description'],
                'parent_id': vals['account_tax_code_id'],
                'is_base': False,
                'company_id': company_id,
                'vat_statement_type':
                vals['type_tax_use'] == 'sale' and 'debit' or
                vals['type_tax_use'] == 'purchase' and 'credit',
                'vat_statement_sign':
                vals['type_tax_use'] == 'sale' and 1 or
                vals['type_tax_use'] == 'purchase' and -1,
            }
            i = 0
            name = vals['name']
            while True:
                if tax_code_obj.search([('name', '=', name),
                                        ('company_id', '=', company_id)]):
                    name += str(i)
                    i += 1
                else:
                    if i > 0:
                        tax_code_vals['name'] += str(i)
                    break
            tax_code = tax_code_obj.create(tax_code_vals)
            vat_account = tax_code.vat_statement_account_id if \
                tax_code.vat_statement_account_id else \
                tax_code.parent_id.vat_statement_account_id if \
                    tax_code.parent_id and tax_code.parent_id. \
                        vat_statement_account_id else False
            vals.update({'tax_code_id': tax_code.id,
                         'ref_tax_code_id': tax_code.id,
                         'account_collected_id': vat_account.id if
                         vat_account else False,
                         'account_paid_id': vat_account.id if
                         vat_account else False,
                         })

        return super(AccountTax, self).create(vals)

    @api.multi
    def write(self, vals):
        tax_code_obj = self.env['account.tax.code']
        company_id = self.company_id.id
        tax = self[0]
        vat_account = False
        if vals.get('name', False):
            if self.search([('name', '=', vals['name']),
                            ('company_id', '=', company_id)]):
                raise Warning(_("Tax name must be unique."))
        if vals.get('description', False):
            if self.search([('description', '=', vals['description']),
                            ('company_id', '=', company_id)]):
                raise Warning(_("Tax description must be unique."))
        if vals.get('type_tax_use', False):
            if vals['type_tax_use'] != tax.type_tax_use:
                raise Warning(_(
                    "Tax Type cannot be changed - create a different tax."))
        if (vals.get('type_tax_use', False) or tax.type_tax_use) == 'sale':
            vals.update({'base_sign': 1, 'tax_sign': 1,
                         'ref_base_sign': -1, 'ref_tax_sign': -1})
        elif (vals.get('type_tax_use', False) or
              tax.type_tax_use) == 'purchase':
            vals.update({'base_sign': -1, 'tax_sign': -1,
                         'ref_base_sign': 1, 'ref_tax_sign': 1})

        if not tax.base_code_id and not tax.parent_id:
            if not vals.get('account_base_tax_code_id', False) and \
                    not tax.account_base_tax_code_id and \
                    not vals.get('base_code_id', False):
                if not tax.tax_code_id or tax.tax_code_id and \
                        not tax.tax_code_id.exclude_from_registries:
                    raise Warning(_("Base Tax Code parent must be set."))
            elif not vals.get('base_code_id', False):
                # missing base tax, so create it
                parent_base_tax_code = tax.account_base_tax_code_id or \
                    tax_code_obj.browse(vals['account_base_tax_code_id'])
                base_tax_code_vals = {
                    'name': tax.name if tax.name else
                    vals.get('name') + ' (imp)',
                    'code': parent_base_tax_code.code + (
                        tax.description if tax.description else
                        vals.get('description')),
                    'parent_id': tax.account_base_tax_code_id.id if
                    tax.account_base_tax_code_id else
                    vals.get('account_base_tax_code_id'),
                    'is_base': True,
                    'company_id': company_id,
                    'vat_statement_type': (
                        tax.type_tax_use or
                        vals.get('type_tax_use')) == 'sale' and 'debit' or (
                            tax.type_tax_use or vals.get(
                                'type_tax_use')) == 'purchase' and 'credit',
                    'vat_statement_sign': (
                        tax.type_tax_use or
                        vals.get('type_tax_use')) == 'sale' and 1 or (
                            tax.type_tax_use or vals.get(
                                'type_tax_use')) == 'purchase' and -1,
                }
                base_code = tax_code_obj.create(base_tax_code_vals)
                vat_account = base_code.vat_statement_account_id if \
                    base_code.vat_statement_account_id else \
                    base_code.parent_id.vat_statement_account_id if \
                    base_code.parent_id and base_code.parent_id. \
                    vat_statement_account_id else False
                vals.update({'base_code_id': base_code.id,
                             'ref_base_code_id': base_code.id})

        if not tax.tax_code_id:
            if not vals.get('account_tax_code_id', False) and \
                    not tax.account_tax_code_id:
                if vat_account:
                    # is a tax without amount - exempt or similar
                    vals.update({'account_collected_id': vat_account.id if
                                 vat_account else False,
                                 'account_paid_id': vat_account.id if
                                 vat_account else False,
                                 })
            elif not vals.get('tax_code_id', False):
                # missing tax, so create it
                parent_tax_code = tax.account_tax_code_id or \
                    tax_code_obj.browse(vals['account_tax_code_id'])
                tax_code_vals = {
                    'name': tax.name or vals.get('name'),
                    'code': parent_tax_code.code + (
                        tax.description if tax.description else
                        vals.get('description')),
                    'parent_id': tax.account_tax_code_id.id if
                    tax.account_tax_code_id else
                    vals.get('account_tax_code_id'),
                    'is_base': False,
                    'company_id': company_id,
                    'vat_statement_type': (
                        tax.type_tax_use or vals.get(
                            'type_tax_use')) == 'sale' and 'debit' or (
                                tax.type_tax_use or vals.get(
                                    'type_tax_use')) == 'purchase' and
                    'credit',
                    'vat_statement_sign': (
                        tax.type_tax_use or vals.get(
                            'type_tax_use')) == 'sale' and 1 or (
                                tax.type_tax_use or vals.get(
                                    'type_tax_use')) == 'purchase' and -1,
                }
                tax_code = tax_code_obj.create(tax_code_vals)
                vat_account = tax_code.vat_statement_account_id if \
                    tax_code.vat_statement_account_id else \
                    tax_code.parent_id.vat_statement_account_id if \
                    tax_code.parent_id and tax_code.parent_id.\
                    vat_statement_account_id else False
                vals.update({'tax_code_id': tax_code.id,
                             'ref_tax_code_id': tax_code.id,
                             'account_collected_id': vat_account.id if
                             vat_account else False,
                             'account_paid_id': vat_account.id if
                             vat_account else False,
                             })

        return super(AccountTax, self).write(vals)

    @api.multi
    def onchange_tax_sign(self, type_tax_use):
        if type_tax_use:
            if type_tax_use == "sale":
                return {'value': {'base_sign': 1, 'tax_sign': 1,
                                  'ref_base_sign': -1, 'ref_tax_sign': -1}}
            elif type_tax_use == "purchase":
                return {'value': {'base_sign': -1, 'tax_sign': -1,
                                  'ref_base_sign': 1, 'ref_tax_sign': 1}}
            elif type_tax_use == "all":
                return {'value': {'base_sign': 1, 'tax_sign': 1,
                                  'ref_base_sign': 1, 'ref_tax_sign': 1}}

    account_tax_code_id = fields.Many2one(
        'account.tax.code', string='Tax Code Parent',
        required=False, help='Parent tax code')
    account_base_tax_code_id = fields.Many2one(
        'account.tax.code', string='Base Tax Code Parent',
        required=False, help='Parent base tax code')
    advanced_view = fields.Boolean('Advanced view')
