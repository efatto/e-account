# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import time
import re
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from collections import defaultdict, Mapping, OrderedDict
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from PIL import Image


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'invoice_tree': self._get_invoice_tree,
            'invoice_move_lines': self._get_invoice_move_lines,
            'ddt': self._get_ddt,
            'ddt_tree': self._get_ddt_tree,
            'set_picking': self._set_picking,
            'line_description': self._line_description,
            'desc_nocode': self._desc_nocode,
            'total_fiscal': self._get_total_fiscal,
            'total_tax_fiscal': self._get_total_tax_fiscal,
            'address_invoice_id': self._get_invoice_address,
            'variant_images': self._variant_images,
            'sale_weight': self._sale_weight,
            'invoice_weight': self._invoice_weight,
            'translate': self._translate_text,
            'img_gray': self._convert_to_gray_scale,
            'get_total_discount': self._get_total_discount,
            'get_total_other': self._get_total_other_amount,
            'get_total_contribution': self._get_total_contribution_amount,
            'get_total_transport': self._get_total_transport_amount,
            'get_total_goods': self._get_total_goods_amount,
            'check_installed_module': self._check_installed_module,
            'get_bank': self._get_bank,
            'get_bank_riba': self._get_bank_riba,
            'transform_forbidden_word': self._transform_forbidden_word,
            'get_product_code': self._get_product_code,
        })
        self.cache = {}

    def _get_invoice_address(self):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid,
                                                      self.ids[0])
        invoice_address = invoice.partner_id
        for address in invoice.partner_id.child_ids:
            if address.type == 'invoice':
                invoice_address = address
        return invoice_address

    def _get_bank_riba(self):
        invoice = self.pool['account.invoice'].browse(
            self.cr, self.uid, self.ids[0])
        has_bank = bank = False
        if invoice.payment_term:
            if invoice.payment_term.line_ids:
                for pt_line in invoice.payment_term.line_ids:
                    if pt_line.type == 'RB':
                        has_bank = True
                        break
            elif invoice.payment_term.type == 'RB':
                has_bank = True
        if has_bank:
            if invoice.bank_riba_id:
                bank = invoice.bank_riba_id
            elif invoice.partner_id.bank_riba_id:
                bank = invoice.partner_id.bank_riba_id
        return bank if bank else []

    def _get_bank(self):
        invoice = self.pool['account.invoice'].browse(
            self.cr, self.uid, self.ids[0])
        company_bank_ids = self.pool['res.partner.bank'].search(
            self.cr, self.uid,
            [('company_id', '=', invoice.company_id.id)],
            order='sequence', limit=1)
        if company_bank_ids:
            company_banks = self.pool['res.partner.bank'].browse(
                self.cr, self.uid, company_bank_ids)
        has_bank = bank = False
        if invoice.payment_term:
            if invoice.payment_term.line_ids:
                for pt_line in invoice.payment_term.line_ids:
                    if pt_line.type != 'RB' or not pt_line.type:
                        has_bank = True
                        break
            elif invoice.payment_term.type != 'RB' \
                    or not invoice.payment_term.type:
                has_bank = True
        if has_bank or not invoice.payment_term:
            if invoice.partner_bank_id:
                bank = invoice.partner_bank_id
            elif invoice.partner_id.company_bank_id:
                bank = invoice.partner_id.company_bank_id
            elif invoice.partner_id.bank_ids:
                bank = invoice.partner_id.bank_ids[0]
            elif invoice.company_id.bank_ids:
                bank = company_banks[0]
        return bank if bank else []

    def _get_total_tax_fiscal(self, tax_line):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        amount_withholding = 0.0
        for line in tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            return invoice.amount_tax - amount_withholding
        return invoice.amount_tax

    def _get_total_fiscal(self, tax_line):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        amount_withholding = 0.0
        for line in tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            return invoice.amount_total - amount_withholding
        return invoice.amount_total

    def _desc_nocode(self, string):
        return re.compile('\[.*\]\ ').sub('', string)

    def _line_description(self, origin):
        sale_order_line_obj = self.pool['sale.order.line']
        stock_picking_obj = self.pool['stock.picking']
        description = []
        if origin and len(origin.split(':')) == 3: # inserire l10n_it_ddt
            sale_order_id = int(origin.split(':')[2])
            sale_order_line = sale_order_line_obj.browse(self.cr, self.uid, sale_order_id)
            description.append(u'Contratto: {name}'.format(name=sale_order_line.order_id.name))
            picking_in_ids = stock_picking_obj.search(self.cr, self.uid, [('type', '=', 'in'), ('rentable', '=', True), ('origin', '=', sale_order_line.order_id.name)])
            picking_out_ids = stock_picking_obj.search(self.cr, self.uid, [('type', '=', 'out'), ('origin', '=', sale_order_line.order_id.name)])
            picking_in = False
            if picking_in_ids:
                picking_in = stock_picking_obj.browse(self.cr, self.uid, picking_in_ids[0])
            if picking_out_ids:
                picking_out = stock_picking_obj.browse(self.cr, self.uid, picking_out_ids[0])
            if picking_out.ddt_number:
                ddt_date = datetime.strptime(picking_out.ddt_date[:10], DEFAULT_SERVER_DATE_FORMAT)
                description.append('Documento di Uscita: {ddt} del {ddt_date}'.format(ddt=picking_out.ddt_number, ddt_date=ddt_date.strftime("%d/%m/%Y")))
            if picking_in:
                ddt_date = datetime.strptime(picking_in.date[:10], DEFAULT_SERVER_DATETIME_FORMAT)
                description.append('Documento di Reso: {ddt} del {ddt_date}'.format(ddt=picking_in.name.replace('-return', ''), ddt_date=ddt_date.strftime("%d/%m/%Y")))

        return '\n'.join(description)

    def _set_picking(self, invoice):
        self._get_invoice_tree(invoice.invoice_line, invoice.stock_picking_package_preparation_ids)
        return False

    def _get_ddt(self):
        def get_picking(picking_name):
            picking_ids = self.pool['stock.picking'].search(self.cr, self.uid, [('name', '=', picking_name)])
            if picking_ids:
                return self.pool['stock.picking'].browse(self.cr, self.uid, picking_ids[0])

        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        if hasattr(invoice, 'move_products') and invoice.move_products:
            return self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        if hasattr(self, 'picking_name'):
            return self.cache.get(self.picking_name, False) or self.cache.setdefault(self.picking_name, get_picking(self.picking_name))
        return False

    @staticmethod
    def get_description(self, ddt_name, ddt_date, order_name, order_date,
                        client_order_ref):
        description = []

        if ddt_name:
            if ddt_date:
                ddt_date = datetime.strptime(
                    ddt_date[:10], DEFAULT_SERVER_DATE_FORMAT)
            description.append(
                self._translate_text(
                    'Our Ref. Picking %s dated %s. %s') % (
                    ddt_name,
                    ddt_date.strftime("%d/%m/%Y") if ddt_date else '',
                    self._translate_text('Your Ref. %s') % client_order_ref if
                    client_order_ref else ''
                ))

        elif order_name:
            # and not self.pool['res.users'].browse(
            #self.cr, self.uid, self.uid).
            # company_id.disable_sale_ref_invoice_report:
            if order_date:
                order_date = datetime.strptime(
                    order_date[:10], DEFAULT_SERVER_DATE_FORMAT)
            description.append(
                self._translate_text(
                    'Our Ref. Order %s dated %s. %s') % (
                    order_name.replace('Consuntivo', ''),
                    order_date.strftime("%d/%m/%Y") if order_date else '',
                    self._translate_text('Your Ref. %s') % client_order_ref if
                    client_order_ref else ''
                ))

        return '\n'.join(description)
    
    # def _get_picking_name(self, line):
    #     picking_obj = self.pool['stock.picking']
    #     picking_ids = picking_obj.search(self.cr, self.uid, [
    #         ('origin', '=', line.origin)])
    #
    #     if len(picking_ids) == 1:
    #         picking = picking_obj.browse(self.cr, self.uid, picking_ids[0])
    #         return picking.name
    #     elif picking_ids:
    #         move_obj = self.pool['stock.move']
    #         move_ids = move_obj.search(self.cr, self.uid, [
    #             ('product_id', '=', line.product_id.id),
    #             ('origin', '=', line.origin)])
    #         if len(move_ids) == 1:
    #             stock_move = move_obj.browse(self.cr, self.uid, move_ids[0])
    #             if stock_move.picking_id:
    #                 return stock_move.picking_id.name
    #             else:
    #                 return False
    #         elif move_ids:
    #             # The same product from the same sale_order is present in
    #             # various picking lists
    #             raise orm.except_orm('Warning', _('Ambiguous line origin'))
    #         else:
    #             return False
    #     else:
    #         return False
    
    def _get_invoice_tree(self, invoice_lines, picking_preparation_ids):
        invoice = {}
        keys = {}
        ddt = False
        sale_order = False
        ddt_date = False
        sale_order_date = False
        client_order_ref = False

        for line in invoice_lines:
            if line.origin:
                if picking_preparation_ids:
                    for picking_preparation in picking_preparation_ids:
                        for picking in picking_preparation.picking_ids:
                            if picking.name == line.origin or \
                                    picking.origin == line.origin:
                                ddt = picking_preparation.ddt_number
                                ddt_date = picking_preparation.date
                                sale_order = picking.sale_id.name
                                sale_order_date = picking.sale_id.date_order
                                client_order_ref = picking.sale_id.\
                                    client_order_ref
                else:
                    sale_order = line.origin
                    sale_order_id = self.pool['sale.order'].search(
                        self.cr, self.uid, [
                            ('name', '=', line.origin),
                            ('company_id', '=', line.company_id.id)
                        ])
                    if sale_order_id and len(sale_order_id) == 1:
                        sale_order_obj = self.pool['sale.order'].browse(
                            self.cr, self.uid, sale_order_id
                        )
                        sale_order_date = sale_order_obj.date_order
                        client_order_ref = sale_order_obj.client_order_ref

            # Order lines by date and by ddt, so first create date_ddt key:
            if ddt:
                if ddt in keys:
                    key = keys[ddt]
                else:
                    key = "{0}_{1}".format(ddt_date, ddt)
            elif sale_order:
                if sale_order in keys:
                    key = keys[sale_order]
                else:
                    key = "{0}_{1}".format(sale_order_date, sale_order)
            else:
                key = False

            if key in invoice:
                invoice[key]['lines'].append(line)
            else:
                description = self.get_description(
                    self, ddt, ddt_date, sale_order, sale_order_date,
                    client_order_ref)
                invoice[key] = {'description': description, 'lines': [line]}
        
        return OrderedDict(
            sorted(invoice.items(), key=lambda t: t[0])).values()

    def _get_ddt_tree(self, sppp_line):
        keys = {}
        order = {}
        description = False
        order_obj = self.pool['sale.order']
        for line in sppp_line:
            if line.move_id:
                # if there is origin get order name and date
                if line.move_id.origin:
                    sale_order_name = line.move_id.origin
                    sale_order_id = order_obj.search(
                        self.cr, self.uid, [('name', '=', sale_order_name)])
                    if sale_order_id:
                        sale_order = order_obj.browse(
                            self.cr, self.uid, sale_order_id[0])
                        order_date = sale_order.date_order
                        order_ref = sale_order.client_order_ref
                    else:
                        order_date = datetime.now().strftime('%Y-%m-%d')
                    sale_order_date = datetime.strptime(
                        order_date[:10], DEFAULT_SERVER_DATE_FORMAT)
                    if sale_order_name in keys:
                        key = keys[sale_order_name]
                    else:
                        key = "{0}_{1}".format(sale_order_date, sale_order_name)
                    description = \
                        'Order ref. %s - %s %s' % (
                            sale_order_name,
                            sale_order_date.strftime("%d/%m/%Y"),
                            ' - ' + order_ref if order_ref else '',
                        )
                # if there is move_id but not origin
                else:
                    key = False
            # if there is not move_id
            else:
                key = False
            # append subsequent lines
            if key in order:
                order[key]['lines'].append(line)
            # create line
            else:
                order[key] = {
                    'description': description,
                    'lines': [line]}

        return OrderedDict(
            sorted(order.items(), key=lambda t: t[0])).values()

    def _get_invoice_move_lines(self, move_id):
        if move_id.line_id:
            return [line for line in move_id.line_id if line.date_maturity]
        else:
            return []

    def _variant_images(self):
        res = False
        if self.pool['ir.config_parameter'].get_param(
                self.cr, self.uid, 'product.print_variant_images',
                default=False):
            res = True
        return res

    def _sale_weight(self):
        res = False
        if self.pool['ir.config_parameter'].get_param(
                self.cr, self.uid, 'sale.print_weight',
                default=False):
            res = True
        return res

    def _invoice_weight(self):
        res = False
        if self.pool['ir.config_parameter'].get_param(
                self.cr, self.uid, 'invoice.print_weight',
                default=False):
            res = True
        return res

    def _translate_text(self, source):
        trans_obj = self.pool['ir.translation']
        lang = 'en_US'
        if self.objects:  # needed?
            lang = self.objects[0].partner_id.lang
        return trans_obj._get_source(
            self.cr, self.uid, 'ir.actions.report.xml', 'report', lang, source)

    def _convert_to_gray_scale(self, base64_source, encoding='base64'):
        if not base64_source:
            return False
        image_stream = StringIO.StringIO(base64_source.decode(encoding))
        image = Image.open(image_stream).convert('LA')
        background_stream = StringIO.StringIO()
        image.save(background_stream, 'PNG')
        return background_stream.getvalue().encode(encoding)

    def _get_total_discount(self, lines):
        total_subprices = total_amount = 0.0
        for line in (l for l in lines if l.discount):
            if isinstance(line._model, type(
                    self.pool['account.invoice.line'])):
                total_amount += line.quantity * line.price_unit
            else:
                total_amount += line.product_uom_qty * line.price_unit
            total_subprices += line.price_subtotal
        for line in (l for l in lines if
                     l.product_id.service_type == 'discount'):
            total_subprices += line.price_subtotal
        return total_amount - total_subprices

    def _get_total_goods_amount(self, lines):
        total_goods_amount = 0.0
        for line in (l for l in lines if not l.is_delivery):
            if not line.product_id.service_type in [
                            'transport', 'contribution', 'other', 'discount']:
                total_goods_amount += line.price_subtotal
        return total_goods_amount

    def _get_total_other_amount(self, lines):
        total_other_amount = 0.0
        for line in (l for l in lines if l.product_id.service_type == 'other'):
            total_other_amount += line.price_subtotal
        return total_other_amount

    def _get_total_contribution_amount(self, lines):
        total_contribution_amount = 0.0
        for line in (l for l in lines if l.product_id.service_type
                     == 'contribution'):
            total_contribution_amount += line.price_subtotal
        return total_contribution_amount

    def _get_total_transport_amount(self, lines):
        total_transport_amount = 0.0
        for line in (l for l in lines if l.product_id.service_type ==
                     'transport' or l.is_delivery and not
                     l.product_id.service_type == 'contribution'):
            total_transport_amount += line.price_subtotal
        return total_transport_amount

    def _check_installed_module(self, module):
        res = False
        if self.pool['ir.module.module'].search(self.cr, self.uid,
                                                [('name', '=', module),
                                                 ('state', '=', 'installed')]):
            res = True
        return res

    def _transform_forbidden_word(self, product, phrase):
        if self._check_installed_module('product_forbidden_word'):
            if product and product.product_forbidden_word_ids and phrase:
                for word in product.product_forbidden_word_ids:
                    phrase = phrase.replace(
                        word.name if word.name else '',
                        word.new_name if word.new_name else '')
        return phrase

    def _get_product_code(self, line):
        code = ''
        if line.product_id and line.product_id.code:
            code = line.product_id.code.replace('XXXX', '')
            for attr_value in line.product_id.attribute_value_ids:
                if attr_value.attribute_id.code_in_report:
                    code = re.sub('[&@#£$][A-Z]',
                                  attr_value.attribute_id.code_in_report, code)
            if line.product_id.product_pack_id:
                code += " | " + line.product_id.product_pack_id.default_code
        #check if product_tmpl_id is possible
        # elif line.product_tmpl_id and line.product_tmpl_id.prefix_code:
        #     code = line.product_tmpl_id.prefix_code.replace('XXXX','')
        return code