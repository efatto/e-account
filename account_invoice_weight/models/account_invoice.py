from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    compute_weight = fields.Selection(
        selection=[
            ("invoice", "On invoice"),
            ("picking", "On picking"),
            ("no", "Manual"),
        ],
        string="Compute weight",
        default="no",
        help="Compute weights and packages:\n"
        "with 'On invoice' the net weight and volume are computed on the invoice lines,"
        " packages and gross weight can be set by user;\n"
        "with 'On picking' all data is computed on pickings;\n"
        "with 'Manual' all data remains those set by user.",
    )
    gross_weight = fields.Float(
        compute="_compute_weight",
        inverse="_inverse_weight",
        help="Computation is done on save.",
    )
    gross_weight_custom = fields.Float()
    volume = fields.Float(
        compute="_compute_weight",
        inverse="_inverse_weight",
        help="Computation is done on save.",
    )
    volume_custom = fields.Float()
    net_weight = fields.Float(
        compute="_compute_weight",
        inverse="_inverse_weight",
        help="Computation is done on save.",
    )
    net_weight_custom = fields.Float()
    packages = fields.Integer(
        compute="_compute_weight",
        inverse="_inverse_weight",
        help="Computation is done on save.",
    )
    packages_custom = fields.Integer()

    @api.depends("compute_weight", "picking_ids", "invoice_line_ids")
    def _compute_weight(self):
        volume_uom_id = self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()
        for invoice in self:
            # sum weight from pickings
            if invoice.compute_weight == "picking" and invoice.picking_ids:
                net_weight = sum(
                    x.net_weight_uom_id._compute_quantity(
                        qty=x.weight, to_unit=invoice.net_weight_uom_id
                    )
                    for x in invoice.picking_ids
                )
                gross_weight = sum(
                    x.gross_weight_uom_id._compute_quantity(
                        qty=x.shipping_weight, to_unit=invoice.gross_weight_uom_id
                    )
                    for x in invoice.picking_ids
                )
                volume = sum(
                    volume_uom_id._compute_quantity(
                        qty=x.volume, to_unit=invoice.volume_uom_id
                    )
                    for x in invoice.picking_ids
                )
                packages = sum(x.number_of_packages for x in invoice.picking_ids)
            # compute from invoice if not pickings or not compute_weight on picking
            elif invoice.compute_weight == "invoice":
                net_weight = sum(
                    inv_line.product_id.weight_uom_id._compute_quantity(
                        qty=(inv_line.product_id.weight or 0) * inv_line.quantity,
                        to_unit=invoice.net_weight_uom_id,
                    )
                    for inv_line in invoice.invoice_line_ids
                )
                # gross_weight obviously does not exist in product
                gross_weight = invoice.gross_weight_custom
                volume = sum(
                    inv_line.product_id.volume_uom_id._compute_quantity(
                        qty=(inv_line.product_id.volume or 0) * inv_line.quantity,
                        to_unit=invoice.volume_uom_id,
                    )
                    for inv_line in invoice.invoice_line_ids
                )
                packages = invoice.packages_custom
            else:
                net_weight = invoice.net_weight_custom
                gross_weight = invoice.gross_weight_custom
                volume = invoice.volume_custom
                packages = invoice.packages_custom
            invoice.net_weight = net_weight
            invoice.gross_weight = gross_weight
            invoice.volume = volume
            invoice.packages = packages

    def _inverse_weight(self):
        for invoice in self:
            if invoice.net_weight:
                invoice.net_weight_custom = invoice.net_weight
            if invoice.gross_weight:
                invoice.gross_weight_custom = invoice.gross_weight
            if invoice.volume:
                invoice.volume_custom = invoice.volume
            if invoice.packages:
                invoice.packages_custom = invoice.packages
