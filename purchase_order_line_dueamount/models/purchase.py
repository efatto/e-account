from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if vals.get('payment_term_id') or vals.get('date_planned'):
                for line in order.order_line:
                    line._refresh_dueamount()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    dueamount_ids = fields.One2many(
        comodel_name='purchase.order.line.dueamount',
        inverse_name='line_id',
        string='Due amount lines',
    )

    @api.model
    def create(self, vals):
        line = super().create(vals)
        line._refresh_dueamount()
        return line

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('price_unit') or vals.get('date_planned') \
                or vals.get('product_qty') or vals.get('discount') \
                or vals.get('discount2') or vals.get('discount3'):
            for line in self:
                line._refresh_dueamount()
        return res

    @api.multi
    def _refresh_dueamount(self):
        self.ensure_one()
        self.dueamount_ids.unlink()
        dueamount_line_obj = self.env['purchase.order.line.dueamount']
        due_line_ids = []
        if self.order_id.payment_term_id and self.price_subtotal:
            totlines = self.order_id.payment_term_id.compute(
                self.price_subtotal,
                self.date_planned or self.order_id.date_planned or
                self.order_id.date_order)[0]
            for dueline in totlines:
                due_line_id = dueamount_line_obj.create({
                    'date': dueline[0],
                    'amount': dueline[1],
                    'line_id': self.id,
                })
                due_line_ids.append(due_line_id.id)
        else:
            due_line_id = dueamount_line_obj.create({
                'date': self.date_planned or self.order_id.date_planned or
                self.order_id.date_order,
                'amount': self.price_subtotal,
                'line_id': self.id,
            })
            due_line_ids.append(due_line_id.id)


class PurchaseOrderLineDueamount(models.Model):
    _name = 'purchase.order.line.dueamount'
    _description = 'Purchase order line due amount'
    _rec_name = 'date'

    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        ondelete='cascade',
        string='Purchase order line',
    )
