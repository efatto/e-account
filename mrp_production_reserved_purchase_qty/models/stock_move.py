from operator import itemgetter
from itertools import groupby

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
        "created_purchase_line_id.state",
        "raw_material_production_id",
        "state",
    )
    def _compute_purchase_ordered_qty(self):
        moves = self.filtered(
            lambda m: m.raw_material_production_id and m.move_orig_ids
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
        # Override to force reservation for production raw component only
        # 1. of MTO procurement for moves without move_orig_ids, probably deleted as
        # available in stock or re-created directly so not linked anymore
        # 2. of MTO procurement which incoming moves are in 'reserved' state, as the
        # original method consider only 'done' state
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
                move.location_id.should_bypass_reservation()
                or move.product_id.type == 'consu'
                or not move.raw_material_production_id
            ):
                continue
            if not move.move_orig_ids:
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
            else:
                # Override original function only to get 'assigned' in stock move as
                # valid for reservation
                move_lines_in = move.move_orig_ids.filtered(
                    lambda m: m.state == 'assigned').mapped('move_line_ids')
                keys_in_groupby = [
                    'location_dest_id', 'lot_id', 'result_package_id', 'owner_id']

                def _keys_in_sorted(ml):
                    return (
                    ml.location_dest_id.id, ml.lot_id.id, ml.result_package_id.id,
                    ml.owner_id.id)

                grouped_move_lines_in = {}
                for k, g in groupby(sorted(move_lines_in, key=_keys_in_sorted),
                                    key=itemgetter(*keys_in_groupby)):
                    qty_done = 0
                    for ml in g:
                        qty_done += ml.product_uom_id._compute_quantity(
                            ml.product_uom_qty, ml.product_id.uom_id)  # original was qty_done
                    grouped_move_lines_in[k] = qty_done
                move_lines_out_done = (
                        move.move_orig_ids.mapped('move_dest_ids') - move) \
                    .filtered(lambda m: m.state in ['done']) \
                    .mapped('move_line_ids')
                # As we defer the write on the stock.move's state at the end of the loop
                # , there could be moves to consider in what our siblings already took.
                moves_out_siblings = move.move_orig_ids.mapped('move_dest_ids') - move
                moves_out_siblings_to_consider = moves_out_siblings & (
                        assigned_moves + partially_available_moves)
                reserved_moves_out_siblings = moves_out_siblings.filtered(
                    lambda m: m.state in ['partially_available', 'assigned'])
                move_lines_out_reserved = (
                        reserved_moves_out_siblings | moves_out_siblings_to_consider
                ).mapped('move_line_ids')
                keys_out_groupby = ['location_id', 'lot_id', 'package_id', 'owner_id']

                def _keys_out_sorted(ml):
                    return (
                    ml.location_id.id, ml.lot_id.id, ml.package_id.id, ml.owner_id.id)

                grouped_move_lines_out = {}
                for k, g in groupby(sorted(move_lines_out_done, key=_keys_out_sorted),
                                    key=itemgetter(*keys_out_groupby)):
                    qty_done = 0
                    for ml in g:
                        qty_done += ml.product_uom_id._compute_quantity(
                            ml.qty_done, ml.product_id.uom_id)
                    grouped_move_lines_out[k] = qty_done
                for k, g in groupby(
                    sorted(move_lines_out_reserved, key=_keys_out_sorted),
                    key=itemgetter(*keys_out_groupby)):
                    grouped_move_lines_out[k] = sum(
                        self.env['stock.move.line'].concat(*list(g)).mapped(
                            'product_qty'))
                available_move_lines = {
                    key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0)
                    for key in grouped_move_lines_in.keys()}
                # pop key if the quantity available amount to 0
                available_move_lines = dict(
                    (k, v) for k, v in available_move_lines.items() if v)

                if not available_move_lines:
                    continue
                for move_line in move.move_line_ids.filtered(lambda m: m.product_qty):
                    if available_move_lines.get((
                                                move_line.location_id, move_line.lot_id,
                                                move_line.result_package_id,
                                                move_line.owner_id)):
                        available_move_lines[(move_line.location_id, move_line.lot_id,
                                              move_line.result_package_id,
                                              move_line.owner_id)
                        ] -= move_line.product_qty
                for (location_id, lot_id, package_id,
                     owner_id), quantity in available_move_lines.items():
                    need = move.product_qty - sum(
                        move.move_line_ids.mapped('product_qty'))
                    # `quantity` is what is brought by chained done move lines. We
                    # double check here this quantity is available on the quants
                    # themselves. If not, this could be the result of an inventory
                    # adjustment that removed totally of partially `quantity`.
                    # When this happens, we chose to reserve the maximum
                    # still available. This situation could not happen on MTS move,
                    # because in this case `quantity` is directly the quantity on the
                    # quants themselves.
                    available_quantity = self.env[
                        'stock.quant'
                    ]._get_available_quantity(
                        move.product_id, location_id, lot_id=lot_id,
                        package_id=package_id, owner_id=owner_id, strict=True
                    )
                    if float_is_zero(available_quantity, precision_rounding=rounding):
                        continue
                    taken_quantity = move._update_reserved_quantity(
                        need, min(quantity, available_quantity),
                        location_id, lot_id,
                        package_id,
                        owner_id)
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    if float_is_zero(
                        need - taken_quantity, precision_rounding=rounding
                    ):
                        assigned_moves |= move
                        break
                    partially_available_moves |= move
        self.env['stock.move.line'].create(move_line_vals_list)
        partially_available_moves.write({'state': 'partially_available'})
        assigned_moves.write({'state': 'assigned'})
        self.mapped('picking_id')._check_entire_pack()
