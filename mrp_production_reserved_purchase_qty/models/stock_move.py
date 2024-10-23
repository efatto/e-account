from odoo import models, api, fields
from odoo.tools import float_is_zero, float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_ordered_qty = fields.Float(
        string='Purchase Ordered Qty',
        compute="_compute_purchase_ordered_qty",
        store=True,
    )

    @api.depends(
        "move_orig_ids",
        "move_orig_ids.move_line_ids",
        "move_orig_ids.move_line_ids.product_qty",
        "raw_material_production_id",
        "state",
    )
    def _compute_purchase_ordered_qty(self):
        moves = self.filtered(
            lambda m: m.raw_material_production_id and m.move_orig_ids
            and m.state != "cancel"
        )
        # removed as not sure if it is needed, from api.depends and filtered:
        # "move_orig_ids.purchase_line_id.procurement_group_id",
        # "and m.move_orig_ids.purchase_line_id.procurement_group_id == m.group_id"
        for move in (self - moves):
            move.purchase_ordered_qty = 0
        for move in moves:
            purchase_ordered_qty = sum(
                move.mapped('move_orig_ids.move_line_ids.product_qty'))
            move.purchase_ordered_qty = purchase_ordered_qty

    def _action_assign(self):
        # Override to force reservation of MTO procurement for moves without
        # move_orig_ids, probably deleted as available in stock or re-created directly
        # so not linked anymore
        super()._action_assign()
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        # Read the `reserved_availability` field of the moves out of the loop to
        # prevent unwanted cache invalidation when actually reserving the move.
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        for move in self:
            rounding = roundings[move]
            missing_reserved_uom_quantity = move.product_uom_qty - \
                                            reserved_availability[move]
            missing_reserved_quantity = move.product_uom._compute_quantity(
                missing_reserved_uom_quantity, move.product_id.uom_id,
                rounding_method='HALF-UP')
            if (
                not move.location_id.should_bypass_reservation()
                and not move.product_id.type == 'consu'
                and not move.move_orig_ids
            ):
                if move.procure_method == 'make_to_order':
                    pass # THIS IS THE ONLY CHANGE OF THE ORIGINAL METHOD
                # If we don't need any quantity, consider the move assigned.
                need = missing_reserved_quantity
                if float_is_zero(need, precision_rounding=rounding):
                    assigned_moves |= move
                    continue
                # Reserve new quants and create move lines accordingly.
                forced_package_id = move.package_level_id.package_id or None
                available_quantity = self.env['stock.quant']._get_available_quantity(
                    move.product_id, move.location_id, package_id=forced_package_id)
                if available_quantity <= 0:
                    continue
                taken_quantity = move._update_reserved_quantity(
                    need, available_quantity, move.location_id,
                    package_id=forced_package_id, strict=False)
                if float_is_zero(taken_quantity, precision_rounding=rounding):
                    continue
                if float_compare(
                    need, taken_quantity, precision_rounding=rounding
                ) == 0:
                    assigned_moves |= move
                else:
                    partially_available_moves |= move
        self.env['stock.move.line'].create(move_line_vals_list)
        partially_available_moves.write({'state': 'partially_available'})
        assigned_moves.write({'state': 'assigned'})
        self.mapped('picking_id')._check_entire_pack()
