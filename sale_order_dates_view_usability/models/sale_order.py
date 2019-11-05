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
                order.requested_date = fields.Datetime.to_string(
                    fields.Datetime.from_string(fields.Datetime.now())
                    + relativedelta(days=int(
                        self.env['ir.config_parameter'].get_param(
                            'sale_default_lead_days'))
                    )
                )
        res = super(SaleOrder, self).action_button_confirm()
        return res

    requested_date = fields.Datetime(
        readonly=False,
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
        copy=False,
        help="If not set, it will be filled at the confirmation of sale order to "
             "(today + sale_default_lead_days parameter).")
