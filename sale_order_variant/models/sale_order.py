# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api, _, exceptions
import re


class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line', "product.configurator"]
    _name = "sale.order.line"

    product_template_id = fields.Many2one('product.template')
    product_template_image = fields.Binary(
        related='product_template_id.image_medium')
    product_attribute_line_id = fields.Many2one(
        'product.attribute.line',
        domain="[('product_tmpl_id','=',product_template_id)]"
        )
    product_attribute_line_stitching_id = fields.Many2one(
        'product.attribute.line',
        domain="[('product_tmpl_id','=',product_template_id)]"
        )
    stitching_value_ids = fields.Many2many(
        string='Values',
        related='product_attribute_line_stitching_id.value_ids',
        readonly=True)
    stitching_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('id', 'in', stitching_value_ids[0][2])]"
    )
    product_attribute_child_ids = fields.One2many(
        string='Childs',
        related='product_attribute_line_id.attribute_id.child_ids',
        readonly=True)
    product_attribute_child_id = fields.Many2one(
        'product.attribute',
        domain="[('id', 'in', product_attribute_child_ids[0][2])]"
    )
    product_attribute_value_ids = fields.Many2many(
        string='Values',
        related='product_attribute_line_id.value_ids',
        readonly=True)
    product_attribute_value_id = fields.Many2one(
        'product.attribute.value',
        domain="[('id', 'in', product_attribute_value_ids[0][2])]"
    )
    product_attribute_image = fields.Binary(
        related='product_attribute_value_id.image')
    product = fields.Char()

    @api.multi
    def _set_product_template(self, product_template):
        self.product_template_id = product_template
        # clean all children fields
        self.product_attribute_line_id = \
            self.product_attribute_child_id = \
            self.product_attribute_value_id = \
            False

    @api.multi
    def _set_material_color(self, material, color):
        attribute = self.env['product.attribute'].search(
            [('code', '=', material)])
        # first search if material has parent
        if attribute and attribute.parent_id:
            # it's a child attribute: set in one passage the attribute line
            # from parent of attribute, and the product_attribute_child_id
            for attribute_line in self.product_template_id. \
                    attribute_line_ids:
                product_attribute_child = \
                    attribute_line.attribute_id.child_ids.filtered(
                        lambda x: x.code == material)
                if product_attribute_child:
                    self.product_attribute_child_id = \
                        product_attribute_child
                    self.product_attribute_line_id = self. \
                        product_template_id.attribute_line_ids.filtered(
                        lambda x: x.attribute_id ==
                                  product_attribute_child.parent_id)
                    self._get_color(color)
                    return
        elif attribute and not attribute.parent_id:
            product_attribute_line = self.product_template_id. \
                attribute_line_ids.filtered(
                    lambda x: x.attribute_id.code == material)
            if product_attribute_line:
                self.product_attribute_line_id = product_attribute_line
                self._get_color(color)

    def _get_color(self, color):
        if self.product_attribute_child_id:
            product_attribute_value = self.product_attribute_child_id. \
                value_ids.filtered(lambda x: x.code == color)
        else:
            product_attribute_value = self.product_attribute_line_id.\
                value_ids.filtered(lambda x: x.code == color)
        if product_attribute_value:
            self.product_attribute_value_id = product_attribute_value
        else:
            self.product_attribute_value_id = False
            raise exceptions.ValidationError('Material color not found')

    def _get_stitching(self, stitching):
        if self.product_attribute_child_id and self.product_attribute_value_id:
            product_attribute_line = self.product_template_id.\
                attribute_line_ids.filtered(
                    lambda x: x.attribute_id.code == 'ST')
            if product_attribute_line:
                self.product_attribute_line_stitching_id = product_attribute_line
                stitching_id = product_attribute_line.value_ids.filtered(
                    lambda x: x.code == stitching
                )
                if stitching_id:
                    self.stitching_value_id = stitching_id
            else:
                self.product_attribute_line_stitching_id = False
                raise exceptions.ValidationError('Material color not found')

    @api.onchange('product')
    def onchange_product(self):
        product_id = False
        if self.product:
            product_obj = self.env['product.product']

            # check if written manually
            if not self.product_attribute_value_id and not self.product_template_id:
                # search attribute-child type
                child_attributes = re.search(
                    '[A-Z][0-9]{2}ST[0-9]{2}', self.product.upper())
                if child_attributes:
                    product_template = self.env['product.template'].search(
                        [('prefix_code', '=',
                          self.product.upper().split(child_attributes.group(0))[0])])
                    if product_template:
                        self._set_product_template(product_template)
                    self._set_material_color(
                        child_attributes.group(0)[0], child_attributes.group(0)[1:3])
                    self._get_stitching(child_attributes.group(0)[5:7])

                # serch attribute type only
                else:
                    attributes = re.search(
                        '[0-9]{6}[A-Z][0-9]{2}', self.product.upper())
                    if attributes:
                        product_template = self.env['product.template'].search(
                            [('prefix_code', '=',
                              self.product.upper().split(
                                  attributes.group(0))[0])])
                        if product_template:
                            self._set_product_template(product_template)
                        # material-color 10 T35
                        self._set_material_color(
                            attributes.group(0)[0:1], attributes.group(0)[1:4])
                if not self.product_attribute_value_id:
                    raise exceptions.ValidationError(
                        _('Code is not valid!')
                    )

            # then search product - if it is attribute-child
            if self.product_template_id and self.product_attribute_child_id \
                    and self.product_attribute_value_id \
                    and self.stitching_value_id:
                domain = product_obj._build_attributes_domain(
                    self.product_template_id, [
                        {'value_id': self.product_attribute_value_id.id},
                        {'value_id': self.stitching_value_id.id}])
                product_id = product_obj.search(domain[0])
                if not product_id:
                    product_id = product_obj.create({
                        'product_tmpl_id': self.product_template_id.id,
                        'attribute_value_ids':
                            [(6, 0,
                              [self.product_attribute_value_id.id,
                               self.stitching_value_id.id])]
                    })

            # attribute type only
            if self.product_template_id and not self.product_attribute_child_id:
                product_id = product_obj.search([
                    ('product_tmpl_id', '=', self.product_template_id.id),
                    ('attribute_value_ids', '=',
                     self.product_attribute_value_id.id)
                ])
                if not product_id:
                    product_id = product_obj.create({
                        'product_tmpl_id': self.product_template_id.id,
                        'attribute_value_ids':
                            [(6, 0,
                              [self.product_attribute_value_id.id])]
                    })
        if product_id:
            if len(product_id) != 1:
                raise exceptions.ValidationError(
                    'Found more than 1 product, product template has malformed'
                    ' variants.'
                )
            # price_unit = self._get_price_unit() or 0.0
            self.product_tmpl_id = product_id.product_tmpl_id
            # self.product_attribute_ids = product_id.attribute_value_ids.ids
            self.product_id = product_id
            self.update_attributes_from_product()

            # clean fields invisibles
            self.product_template_id = \
                self.product_attribute_line_id = \
                self.product_attribute_line_stitching_id = \
                self.stitching_value_id = \
                self.product_attribute_child_id = \
                self.product_attribute_value_id = \
                False

    @api.multi
    def update_attributes_from_product(self):
        # First, empty current list
        self.product_attribute_ids = [
            (2, x.id) for x in self.product_attribute_ids]
        if self.product_id:
            attribute_list = (
                self.product_id._get_product_attributes_values_dict())
            for val in attribute_list:
                val['product_tmpl_id'] = self.product_id.product_tmpl_id
                val['owner_model'] = self._name
                val['owner_id'] = self.id
            product = self.product_id
            if self._fields.get('partner_id'):
                # If our model has a partner_id field, language is got from it
                product = self.env['product.product'].with_context(
                    lang=self.partner_id.lang).browse(self.product_id.id)
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
            self.name = self._get_product_description(
                product.product_tmpl_id, product, product.attribute_value_ids)

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        # Get child_ids attribute if present
        # First, empty current list
        self.product_attribute_ids = [
            (2, x.id) for x in self.product_attribute_ids]
        if not self.product_tmpl_id.attribute_line_ids:
            self.product_id = self.product_tmpl_id.product_variant_ids
        else:
            if not self.product and not \
                    self.env.context.get('not_reset_product'):
                self.product_id = False
            attribute_list = []
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                #changed for parent stuff
                if attribute_line.attribute_id.child_ids:
                    for child in attribute_line.attribute_id.child_ids:
                        attribute_list.append({
                            'attribute_id': child.id,
                            'product_tmpl_id': self.product_tmpl_id.id,
                            'owner_model': self._name,
                            'owner_id': self.id,
                        })
                #end of change
                else:
                    attribute_list.append({
                        'attribute_id': attribute_line.attribute_id.id,
                        'product_tmpl_id': self.product_tmpl_id.id,
                        'owner_model': self._name,
                        'owner_id': self.id,
                    })
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
        # Needed because the compute method is not triggered
        self.product_attribute_ids._compute_possible_value_ids()
        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}
