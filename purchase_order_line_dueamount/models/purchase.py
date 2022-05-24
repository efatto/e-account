from odoo import api, models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    dueamount_ids = fields.Many2many(
        compute='_compute_dueamount_ids',
        comodel_name='purchase.order.line.dueamount',
        string='Due amount lines',
        store=True,
    )

    @api.multi
    @api.depends('order_id.payment_term_id', 'date_planned')
    def _compute_dueamount_ids(self):
        dueamount_line_obj = self.env['purchase.order.line.dueamount']
        for line in self:
            due_line_ids = []
            if line.order_id.payment_term_id and line.price_subtotal:
                totlines = line.order_id.payment_term_id.compute(
                    line.price_subtotal,
                    line.date_planned or line.order_id.date_planned or
                    line.order_id.date_order)[0]
                for dueline in totlines:
                    due_line_id = dueamount_line_obj.create({
                        'date': dueline[0],
                        'amount': dueline[1],
                    })
                    due_line_ids.append(due_line_id.id)
            else:
                due_line_id = dueamount_line_obj.create({
                    'date': line.date_planned or line.order_id.date_planned or
                    line.order_id.date_order,
                    'amount': line.price_subtotal,
                })
                due_line_ids.append(due_line_id.id)
            line.dueamount_ids = dueamount_line_obj.browse(due_line_ids)


class PurchaseOrderLineDueamount(models.Model):
    _name = 'purchase.order.line.dueamount'
    _description = 'Purchase order line due amount'
    _rec_name = 'date'

    amount = fields.Float(required=True)
    date = fields.Date(required=True)
