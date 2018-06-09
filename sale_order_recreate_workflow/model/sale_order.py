# -*- coding: utf-8 -*-
from openerp import fields, models, api
from openerp.tools.translate import _


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def recreate_workflow(self):
        self.ensure_one()
        self.delete_workflow()
        self.create_workflow()
        self.write({'state': 'draft'})
        self.order_line.write({'state': 'draft'})
        self.mapped('order_line.procurement_ids').write(
            {'sale_line_id': False})
        msg = _('Order workflow recreated')
        self.message_post(body=msg)
