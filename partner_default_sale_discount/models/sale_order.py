# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, exceptions, _
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    default_sale_discount = fields.Float(
        string="Default sales discount (%)")
    default_sale_complex_discount = fields.Char(
        'Complex Discount',
        size=32,
        help='E.g.: 15.5+5, or 50+10+3.5')

    @api.onchange('default_sale_complex_discount', 'default_sale_discount')
    def onchange_discounts(self):
        net = 0.0
        if self.default_sale_complex_discount:
            complex_discount = self.default_sale_complex_discount.replace(
                '%', '').replace(',', '.').replace('-', '+').replace(' ', '+')
            for disc in complex_discount.split('+'):
                try:
                    net = 100 - ((100.00 - net) * (100.00 - float(disc)) / 100)
                except:
                    exceptions.ValidationError(_('Bad discount format'))
        else:
            net = self.default_sale_discount
        self.default_sale_discount = net

    @api.multi
    def onchange_partner_id(self, part):
        res = super(SaleOrder, self).onchange_partner_id(part)
        if part:
            partner_id = self.env['res.partner'].browse(part)
            res['value'].update(
                {'default_sale_discount': partner_id.default_sale_discount,
                 'default_sale_complex_discount': partner_id.
                     default_sale_complex_discount})
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Inject the default in the context of the line this way for
        making it inheritable.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu
        )
        if view_type != 'form':  # pragma: no cover
            return res
        eview = etree.fromstring(res['arch'])
        xml_order_line = eview.xpath("//field[@name='order_line']")
        xml_discount = eview.xpath("//field[@name='default_sale_discount']")
        xml_complex_discount = eview.xpath(
            "//field[@name='default_sale_complex_discount']")
        if xml_order_line and xml_discount:
            # This should be handled in "string" mode, as the context can
            # contain a expression that can only be evaled on execution time
            # on the JS web client
            context = xml_order_line[0].get('context', '{}').replace(
                "{", "{'default_discount': default_sale_discount, ", 1
            )
            if xml_complex_discount:
                context = context.replace(
                    "{", "{'default_complex_discount':"
                         " default_sale_complex_discount, ", 1
                )
            xml_order_line[0].set('context', context)
            res['arch'] = etree.tostring(eview)
        return res

    @api.multi
    @api.depends('default_sale_discount', 'order_line')
    def sale_discount_update(self):
        for order in self:
            for line in order.order_line:
                line.discount = order.default_sale_discount
                line.complex_discount = order.default_sale_complex_discount
