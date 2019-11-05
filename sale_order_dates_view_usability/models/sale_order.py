# -*- encoding: utf-8 -*-

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for order in self:
            if self.env['ir.config_parameter'].get_param('sale_default_lead_days') and \
                    not order.requested_date:
                order.requested_date = fields.Date.to_string(
                    fields.Date.from_string(fields.Date.today())
                    + relativedelta(days=int(
                        self.env['ir.config_parameter'].get_param(
                            'sale_default_lead_days'))
                    )
                )
        res = super(SaleOrder, self).action_button_confirm()
        return res

    requested_date = fields.Date(
        readonly=False,
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
        copy=False,
        help="If not set, it will be filled at the confirmation of sale order to "
             "(today + sale_default_lead_days parameter).")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    requested_date = fields.Date()
