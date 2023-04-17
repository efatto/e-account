from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for order in self:
            if vals.get('payment_term_id') or vals.get('commitment_date'):
                for line in order.order_line:
                    line._refresh_dueamount()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dueamount_ids = fields.One2many(
        comodel_name='sale.order.line.dueamount',
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
        if vals.get('price_unit') or vals.get('commitment_date') \
                or vals.get('product_uom_qty') or vals.get('discount') \
                or vals.get('discount2') or vals.get('discount3'):
            for line in self:
                line._refresh_dueamount()
        return res

    @api.multi
    def _refresh_dueamount(self):
        self.ensure_one()
        self.dueamount_ids.unlink()
        dueamount_line_obj = self.env['sale.order.line.dueamount']
        due_line_ids = []
        if self.order_id.payment_term_id and self.price_subtotal:
            totlines = self.order_id.payment_term_id.compute(
                self.price_total,
                self.commitment_date or self.order_id.commitment_date or
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
                'date': self.commitment_date or self.order_id.commitment_date or
                self.order_id.date_order,
                'amount': self.price_total,
                'line_id': self.id,
            })
            due_line_ids.append(due_line_id.id)


class SaleOrderLineDueamount(models.Model):
    _name = 'sale.order.line.dueamount'
    _description = 'Sale order line due amount'
    _rec_name = 'date'

    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    invoiced_percent = fields.Float(
        compute='_compute_invoiced_percent', store=True
    )
    currency_rate = fields.Float(
        related='line_id.order_id.currency_id.rate'
    )
    line_id = fields.Many2one(
        comodel_name='sale.order.line',
        ondelete='cascade',
        string='Sale order line',
    )

    @api.multi
    @api.depends('line_id.qty_invoiced', 'line_id.product_uom_qty')
    def _compute_invoiced_percent(self):
        for line in self:
            line.invoiced_percent = line.line_id.qty_invoiced / (
                line.line_id.product_uom_qty or 1)
