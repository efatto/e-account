# -*- coding: utf-8 -*-
from openerp import models, fields


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'reminder']
    _reminder_date_field = 'requested_date'
    _reminder_description_field = 'name'

    reminder_alarm_ids = fields.Many2many(string='Next Action Reminders')
