# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

import time
import re
from openerp import _
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil import tz
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
            'ddt_tree': self._get_ddt_tree,
            'desc_nocode': self._desc_nocode,
            'total_fiscal': self._get_total_fiscal,
            'total_tax_fiscal': self._get_total_tax_fiscal,
            'get_initial_residual': self._get_initial_residual,
            'address_invoice_id': self._get_invoice_address,
            'variant_images': self._variant_images,
            'sale_weight': self._sale_weight,
            'invoice_weight': self._invoice_weight,
            'footer_header': self._footer_header,
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
            'get_group_tax': self._get_group_tax,
            'is_printable_invoice_line_tax': self.
                _is_printable_invoice_line_tax,
            'has_complex_discount': self._has_complex_discount,
        })
        self.cache = {}

    def _get_invoice_address(self, model='account.invoice'):
        obj = self.pool[model].browse(self.cr, self.uid, self.ids[0])
        invoice_address = obj.partner_id
        for address in obj.partner_id.child_ids:
            if address.type == 'invoice':
                invoice_address = address
        return invoice_address

    def _get_bank_riba(self, model='account.invoice'):
        obj = self.pool[model].browse(
            self.cr, self.uid, self.ids[0])
        has_bank = bank = False
        if obj.payment_term:
            if obj.payment_term.line_ids:
                for pt_line in obj.payment_term.line_ids:
                    if pt_line.type == 'RB':
                        has_bank = True
                        break
            if obj.payment_term.type == 'RB':
                has_bank = True
        if has_bank:
            if model == 'account.invoice':
                if obj.bank_riba_id:
                    bank = obj.bank_riba_id
            if not bank:
                if obj.commercial_partner_id.bank_riba_id:
                    bank = obj.commercial_partner_id.bank_riba_id
        return bank if bank else []

    def _get_bank(self, model='account.invoice'):
        obj = self.pool[model].browse(
            self.cr, self.uid, self.ids[0])
        company_bank_ids = self.pool['res.partner.bank'].search(
            self.cr, self.uid,
            [('company_id', '=', obj.company_id.id)],
            order='sequence', limit=1)
        has_bank = bank = False
        if obj.payment_term:
            if obj.payment_term.line_ids:
                for pt_line in obj.payment_term.line_ids:
                    if pt_line.type != 'RB' or not pt_line.type:
                        has_bank = True
                        break
            elif obj.payment_term.type != 'RB' \
                    or not obj.payment_term.type:
                has_bank = True
        if has_bank or not obj.payment_term:
            if model == 'account.invoice':
                if obj.partner_bank_id:
                    bank = obj.partner_bank_id
            if not bank:
                if obj.commercial_partner_id.company_bank_id:
                    bank = obj.commercial_partner_id.company_bank_id
                elif obj.commercial_partner_id.bank_ids:
                    bank = obj.commercial_partner_id.bank_ids[0]
                elif obj.company_id.bank_ids and not \
                        self.pool['ir.config_parameter'].get_param(
                        self.cr, self.uid, 'report.not.print.default.bank',
                        default=False):
                    if company_bank_ids:
                        company_banks = self.pool['res.partner.bank'].browse(
                            self.cr, self.uid, company_bank_ids)
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

    def _get_initial_residual(self, tax_line):
        invoice = self.pool['account.invoice'].browse(self.cr, self.uid, self.ids[0])
        amount_excluded = 0.0
        for line in tax_line:
            if line.tax_code_id.exclude_from_registries:
                amount_excluded += line.tax_amount
        if amount_excluded != 0.0:
            return invoice.amount_total + amount_excluded
        return invoice.amount_total

    def _desc_nocode(self, string):
        return re.compile('\[.*\] ').sub('', string)

    @staticmethod
    def get_description(self, ddt_name, ddt_date, order_name, order_date,
                        client_order_ref, ddt_id, mrp_name, mrp_date,
                        mrp_machine, mrp_frame, mrp_onsite_name,
                        mrp_onsite_date, mrp_onsite_machine, mrp_onsite_frame):
        description = []
        if order_date:
            order_date = self._convert_datetime_to_date_tz(order_date)
        if ddt_date:
            ddt_date = datetime.strptime(ddt_date, DEFAULT_SERVER_DATE_FORMAT)
        if ddt_name:
            description.append(
                _('Our Ref. Picking %s dated %s. %s %s %s')
                % (
                    ddt_name,
                    ddt_date.strftime("%d/%m/%Y") if ddt_date else '',
                    (_('Our ref. %s dated %s.'
                       ) % (order_name, order_date)
                     ) if order_name and not mrp_name else '',
                    (_('Your Ref. %s.') % client_order_ref
                     ) if client_order_ref and ddt_id else '',
                    (_('Ref. Our Order %s dated %s. Machine: %s frame %s.'
                       ) % (mrp_name, mrp_date, mrp_machine, mrp_frame)
                     ) if mrp_name else '',
                )
            )

        elif order_name:
            description.append(
                _('Our Ref. Order %s %s %s %s') % (
                    order_name,
                    (_(' dated %s') % order_date) if
                    order_date else '',
                    (_('.Your Ref. %s') % client_order_ref) if
                    client_order_ref else '',
                    (_(' dated %s. Machine: %s frame %s') % (
                        mrp_onsite_date,
                        mrp_onsite_machine, mrp_onsite_frame)
                     ) if mrp_onsite_name else '',
                ))

        return '\n'.join(description)

    def _convert_datetime_to_date_tz(self, date):
        to_zone = tz.gettz(self.localcontext['tz'])
        from_zone = tz.tzutc()
        date_tz = datetime.strptime(
            date, DEFAULT_SERVER_DATETIME_FORMAT
                ).replace(tzinfo=from_zone).astimezone(
                    to_zone).strftime("%d/%m/%Y")
        return date_tz

    def _get_invoice_tree(self, invoice_lines, picking_preparation_ids):
        invoice = keys = {}
        ddt_date = client_order_ref = ddt_id = False

        for line in invoice_lines:
            rental_ddt = rental_ddt_date = return_pick_date = ddt = key = \
                sale_order = sale_order_date = mrp_name = mrp_date = \
                mrp_machine = mrp_frame = mrp_onsite_name = mrp_onsite_date = \
                mrp_onsite_machine = mrp_onsite_frame = False
            if line.origin:
                for picking_preparation in picking_preparation_ids:
                    for picking in picking_preparation.picking_ids:
                        if picking.name == line.origin or \
                                picking.origin == line.origin:
                            ddt_id = picking_preparation.id
                            ddt = picking_preparation.ddt_number
                            ddt_date = picking_preparation.date
                            sale_order = picking.origin
                            if self._check_installed_module(
                                    'mrp_repair_management'):
                                mrp_id = self.pool['mrp.repair'].search(
                                    self.cr, self.uid, [
                                        ('out_picking_id', '=', picking.id)
                                    ])
                                if mrp_id:
                                    mrp = self.pool['mrp.repair'].browse(
                                        self.cr, self.uid, mrp_id
                                    )
                                    mrp_name = mrp.name
                                    mrp_date = self.\
                                        _convert_datetime_to_date_tz(
                                            mrp.date)
                                    mrp_machine = mrp.machine_id.name
                                    mrp_frame = mrp.machine_id.frame if \
                                        mrp.machine_id.frame else 'n.d.'
                            break
                if not ddt:
                    # invoice not created from shipment, origin is sale order
                    sale_order = line.origin
                sale_order_id = self.pool['sale.order'].search(
                    self.cr, self.uid, [
                        ('name', '=', sale_order),
                        ('company_id', '=', line.company_id.id)
                    ], limit=1)
                if sale_order_id:
                    sale_order_obj = self.pool['sale.order'].browse(
                        self.cr, self.uid, sale_order_id
                    )
                    sale_order_date = sale_order_obj.date_order
                    client_order_ref = sale_order_obj.client_order_ref
                    if self._check_installed_module('sale_rental_machine'):
                        # add sale rental data if exists
                        for order_line in sale_order_obj.order_line:
                            if order_line.rental_type and \
                                    order_line.order_id.ddt_ids:
                                rental_ddt = order_line.order_id.ddt_ids[
                                    0].ddt_number
                                rental_ddt_date = order_line.order_id.\
                                    ddt_ids[0].date
                                pick_type_in = self.pool['ir.model.data'].\
                                    get_object_reference(
                                        self.cr, self.uid,
                                        'stock', 'picking_type_in')[1]
                                return_pick_id = [
                                    x for x in
                                    order_line.order_id.picking_ids if
                                    x.picking_type_id.id ==
                                    pick_type_in]
                                if return_pick_id and \
                                        return_pick_id[0].date_done:
                                    return_pick_date = \
                                        self._convert_datetime_to_date_tz(
                                            return_pick_id[0].date_done)

                # search mrp without out_picking_id (onsite)
                if self._check_installed_module('mrp_repair_management'):
                    mrp_onsite_id = self.pool['mrp.repair'].search(
                        self.cr, self.uid, [
                            ('name', '=', line.origin)
                        ])
                    if mrp_onsite_id:
                        mrp_onsite = self.pool['mrp.repair'].browse(
                            self.cr, self.uid, mrp_onsite_id
                        )
                        mrp_onsite_name = mrp_onsite.name
                        mrp_onsite_date = self._convert_datetime_to_date_tz(
                                mrp_onsite.date)
                        mrp_onsite_machine = mrp_onsite.machine_id.name
                        mrp_onsite_frame = mrp_onsite.machine_id.frame if \
                            mrp_onsite.machine_id.frame else 'n.d.'
            # Order lines by date and by ddt, so first create date_ddt key:
            if ddt:
                # this row has ddt and possibly sale_order
                if ddt in keys:
                    key = keys[ddt]
                else:
                    key = "{0}_{1}_{2}_{3}".format(ddt_date, ddt,
                                                   sale_order_date, sale_order)
            elif sale_order:
                # this row has only sale order
                if sale_order in keys:
                    key = keys[sale_order]
                else:
                    key = "{0}_{1}_{2}_{3}".format(ddt_date, ddt,
                                                   sale_order_date, sale_order)

            if key in invoice:
                invoice[key]['lines'].append(line)
            else:
                description = self.get_description(
                    self, ddt, ddt_date, sale_order, sale_order_date,
                    client_order_ref, ddt_id, mrp_name, mrp_date, mrp_machine,
                    mrp_frame, mrp_onsite_name, mrp_onsite_date,
                    mrp_onsite_machine, mrp_onsite_frame)
                if rental_ddt and rental_ddt_date:
                    date = datetime.strptime(
                        rental_ddt_date, DEFAULT_SERVER_DATE_FORMAT)
                    description = '\n'.join(
                        [description, _('Outgo document: %s dated %s.%s') %(
                            rental_ddt, date.strftime("%d/%m/%Y"),
                            _(' Date return %s.') % return_pick_date if
                            return_pick_date else ''
                        )]
                    )
                invoice[key] = {'description': description, 'lines': [line]}

        def get_key(t):
            if t[0]:
                return t[0]
            else:
                return 'ZZZ'

        return OrderedDict(sorted(invoice.items(), key=get_key)).values()

    def _get_ddt_tree(self, sppp_line_ids):
        # group sppp lines by sale order if present
        keys = order = {}
        description = order_ref = False
        order_obj = self.pool['sale.order']
        for line in sppp_line_ids:
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
                else: # if there is move_id but not origin
                    key = False
            else: # if there is not move_id
                key = False
            if key in order: # append subsequent lines
                order[key]['lines'].append(line)
            else: # create line
                order[key] = {
                    'description': description,
                    'lines': [line]}

        return OrderedDict(
            sorted(order.items(), key=lambda t: t[0])).values()

    @staticmethod
    def _get_group_tax(tax_lines):
        tax_group = {}
        for tax_line in tax_lines:
            if tax_line.name not in tax_group and \
                    not(tax_line.tax_code_id.notprintable or
                        tax_line.base_code_id.notprintable):
                tax_group[tax_line.name] = {
                    'name': tax_line.name,
                    'base': tax_line.base,
                    'amount': tax_line.amount}
            elif not(tax_line.tax_code_id.notprintable or
                     tax_line.base_code_id.notprintable):
                tax_group[tax_line.name]['base'] += tax_line.base
                tax_group[tax_line.name]['amount'] += tax_line.amount
        return tax_group.values()

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

    def _footer_header(self):
        res = False
        if self.pool['ir.config_parameter'].get_param(
                self.cr, self.uid, 'report_aeroo.print_footer_header',
                default=False):
            res = True
        return res

    def _translate_text(self, source):
        trans_obj = self.pool['ir.translation']
        lang = 'en_US'
        if self.objects:  # needed?
            lang = self.objects[0].partner_id.lang
        return trans_obj._get_source(
            self.cr, self.uid, 'website', 'view', lang, source)

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
        for line in (l for l in lines if not l.is_delivery and l.product_id):
            if line.product_id.service_type not in [
                    'transport', 'contribution', 'other', 'discount']:
                if isinstance(line._model, type(
                        self.pool['account.invoice.line'])):
                    if self._is_printable_invoice_line_tax(
                            line.invoice_line_tax_id):
                        if self._check_installed_module(
                                'sale_advance_invoice_progress'):
                            if not line.advance_invoice_id:
                                total_goods_amount += line.price_subtotal
                                continue
                        elif self._check_installed_module(
                                'sale_advance_invoice_progress'):
                            if not line.product_id.downpayment:
                                total_goods_amount += line.price_subtotal
                                continue
                        else:
                            total_goods_amount += line.price_subtotal
                else:
                    # if self._is_printable_invoice_line_tax(
                    #         line.tax_id): useful if report is compatible
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

    def _get_product_code(self, line, pack=False):
        code = ''
        template_code = ''
        if line.product_id and line.product_id.code:
            template_code = line.product_id.product_tmpl_id.prefix_code
            code = line.product_id.code.replace('XXXX', '').replace(
                template_code, '')
            for attr_value in line.product_id.attribute_value_ids:
                if attr_value.attribute_id.code_in_report:
                    code_in_report = attr_value.attribute_id.code_in_report
                    if code_in_report.upper() == 'FALSE':
                        code_in_report = ''
                    code = re.sub('[&@#£$§°€][A-Z]', code_in_report, code)
            if pack and line.product_id.product_pack_id:
                code += " | " + line.product_id.product_pack_id.default_code \
                    if line.product_id.product_pack_id.default_code else ''
        #check if product_tmpl_id is possible
        # elif line.product_tmpl_id and line.product_tmpl_id.prefix_code:
        #     code = line.product_tmpl_id.prefix_code.replace('XXXX','')
        return '\n'.join([template_code, code])

    @staticmethod
    def _is_printable_invoice_line_tax(tax_line):
        for line in tax_line:
            # check if at least 1 is printable
            if not (line.tax_code_id.notprintable or
                    line.base_code_id.notprintable):
                return True
        return False

    def _has_complex_discount(self, lines):
        res = False
        if self._check_installed_module('discount_complex'):
            if lines.filtered('complex_discount'):
                res = True
        return res
