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
        default="invoice",
    )
    gross_weight = fields.Float(
        compute="_compute_weight",
        help="The weight is computed when the invoice is done.",
    )
    volume = fields.Float(
        compute="_compute_weight",
        help="The volume is computed when the invoice is done.",
    )
    net_weight = fields.Float(
        compute="_compute_weight",
        help="Put here net weight when computed amount is not correct.",
    )
    packages = fields.Integer(
        compute="_compute_weight",
        help="Put here number of packages when computed amount is not correct.",
    )

    @api.depends("compute_weight", "picking_ids", "invoice_line_ids")
    def _compute_weight(self):
        volume_uom_id = self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()
        for invoice in self:
            net_weight = 0
            gross_weight = 0
            volume = 0
            packages = 0
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
                        qty=inv_line.product_id.weight or 0,
                        to_unit=invoice.net_weight_uom_id,
                    )
                    * inv_line.quantity
                    for inv_line in invoice.invoice_line_ids
                )
                # gross_weight obviously does not exist in product
                gross_weight = net_weight
                volume = sum(
                    inv_line.product_id.volume_uom_id._compute_quantity(
                        qty=inv_line.product_id.volume or 0,
                        to_unit=invoice.volume_uom_id,
                    )
                    * inv_line.quantity
                    for inv_line in invoice.invoice_line_ids
                )
                # packages not computable
            invoice.net_weight = net_weight
            invoice.gross_weight = gross_weight
            invoice.volume = volume
            invoice.packages = packages
