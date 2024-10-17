from odoo import api, models, fields


class CashFlowForecastLine(models.Model):
    _inherit = 'mis.cash_flow.forecast_line'

    mrp_line_id = fields.Many2one(
        comodel_name='stock.move',
        ondelete='cascade',
        string='Mrp row component line',
    )
    mrp_balance_currency = fields.Monetary(
        currency_field='currency_id',
        help='Mrp purchase amount in company currency recomputed with qty to order',
    )
    mrp_reserved_percent = fields.Float(
        compute='_compute_mrp_balance_forecast',
        string="Reserved mrp component (%)",
        store=True
    )
    mrp_balance_forecast = fields.Float(
        compute='_compute_mrp_balance_forecast',
        string='Mrp forecast balance',
        store=True,
    )

    @api.multi
    @api.depends(
        'mrp_balance_currency',
        'mrp_line_id.product_uom_qty',  # equivale a ordinato, è quella da consumare
        'mrp_line_id.reserved_availability',  # equivale a ricevuto, è quella ordinata
        'mrp_line_id.raw_material_production_id.date_planned_start',
        'mrp_line_id.bom_line_id.price_unit',  # da mrp_bom_evaluation
        # 'mrp_line_id.raw_material_production_id.sale_id.date_order', # non serve, vedi
        # sotto
        # "mrp_line_id.raw_material_production_id.sale_id.currency_id.rate", # non c'è
        # una conversione valuta, in quanto il prezzo unitario sulla bom è in valuta
        # aziendale
        # todo se i valori sulla bom line fossero stati convertiti, sarebbe da pensare
        #  come rivalutarli
    )
    def _compute_mrp_balance_forecast(self):
        for line in self:
            mrp_reserved_percent = 0
            if line.mrp_line_id:
                if line.mrp_line_id.product_id.type == "consu":
                    # consumable products are always shown as reserved, but they are
                    # purchased as services at the same time of the other products, so
                    # we set 0 to reserved percent
                    mrp_reserved_percent = 0
                else:
                    mrp_reserved_percent = line.mrp_line_id.reserved_availability / (
                        max(
                            line.mrp_line_id.product_uom_qty,
                            line.mrp_line_id.reserved_availability,
                            1,
                        )
                    )
                mrp_reserved_percent = min(mrp_reserved_percent, 1)
            line.mrp_reserved_percent = mrp_reserved_percent
            line.mrp_balance_forecast = line.mrp_balance_currency
            line.balance = line.mrp_balance_forecast
