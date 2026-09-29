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
    # The shipping fields are provided by l10n_it_accompanying_invoice, here they
    # are made computed to be filled from pickings or invoice lines.
    delivery_gross_weight = fields.Float(
        compute="_compute_weight",
        inverse="_inverse_weight",
        store=True,
        readonly=False,
        help="Computation is done on save.",
    )
    delivery_gross_weight_custom = fields.Float()
    delivery_volume = fields.Float(
        compute="_compute_weight",
        inverse="_inverse_weight",
        store=True,
        readonly=False,
        help="Computation is done on save.",
    )
    delivery_volume_custom = fields.Float()
    delivery_net_weight = fields.Float(
        compute="_compute_weight",
        inverse="_inverse_weight",
        store=True,
        readonly=False,
        help="Computation is done on save.",
    )
    delivery_net_weight_custom = fields.Float()
    delivery_packages = fields.Integer(
        compute="_compute_weight",
        inverse="_inverse_weight",
        store=True,
        readonly=False,
        help="Computation is done on save.",
    )
    delivery_packages_custom = fields.Integer()
    stock_package_ids = fields.Many2many(
        comodel_name="stock.quant.package",
        string="Packages custom",
        compute="_compute_stock_package_ids",
        compute_sudo=True,
        store=True,
    )

    @api.depends("picking_ids.stock_package_ids")
    def _compute_stock_package_ids(self):
        for move in self:
            # remove picking_ids already invoiced with other invoices!
            move.stock_package_ids = move.picking_ids.filtered(
                lambda pick, mo=move: all(
                    mo == m for m in pick.move_ids.mapped("invoice_line_ids.move_id")
                )
            ).mapped("stock_package_ids")

    @api.depends("compute_weight", "picking_ids", "invoice_line_ids")
    def _compute_weight(self):
        volume_uom_id = self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()
        weight_uom_id = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()
        for invoice in self:
            # sum weight from pickings
            if invoice.compute_weight == "picking" and invoice.picking_ids:
                net_weight = sum(
                    weight_uom_id._compute_quantity(
                        qty=pick.shipping_weight,
                        to_unit=invoice.delivery_net_weight_uom_id,
                    )
                    for pick in invoice.picking_ids
                )
                gross_weight = sum(
                    weight_uom_id._compute_quantity(
                        qty=pick.shipping_weight,
                        to_unit=invoice.delivery_gross_weight_uom_id,
                    )
                    for pick in invoice.picking_ids
                )
                volume = sum(
                    volume_uom_id._compute_quantity(
                        qty=pick.volume, to_unit=invoice.delivery_volume_uom_id
                    )
                    for pick in invoice.picking_ids
                )
                packages = sum(pick.number_of_packages for pick in invoice.picking_ids)
            # compute from invoice if not pickings or not compute_weight on picking
            elif invoice.compute_weight == "invoice":
                net_weight = sum(
                    inv_line.product_id.weight_uom_id._compute_quantity(
                        qty=(inv_line.product_id.weight or 0) * inv_line.quantity,
                        to_unit=invoice.delivery_net_weight_uom_id,
                    )
                    for inv_line in invoice.invoice_line_ids
                )
                # gross_weight cannot exist in product
                gross_weight = invoice.delivery_gross_weight_custom
                volume = sum(
                    inv_line.product_id.volume_uom_id._compute_quantity(
                        qty=(inv_line.product_id.volume or 0) * inv_line.quantity,
                        to_unit=invoice.delivery_volume_uom_id,
                    )
                    for inv_line in invoice.invoice_line_ids
                )
                packages = invoice.delivery_packages_custom
            else:
                net_weight = invoice.delivery_net_weight_custom
                gross_weight = invoice.delivery_gross_weight_custom
                volume = invoice.delivery_volume_custom
                packages = invoice.delivery_packages_custom
            invoice.delivery_net_weight = net_weight
            invoice.delivery_gross_weight = gross_weight
            invoice.delivery_volume = volume
            invoice.delivery_packages = packages

    def _inverse_weight(self):
        for invoice in self:
            invoice.delivery_net_weight_custom = invoice.delivery_net_weight
            invoice.delivery_gross_weight_custom = invoice.delivery_gross_weight
            invoice.delivery_volume_custom = invoice.delivery_volume
            invoice.delivery_packages_custom = invoice.delivery_packages
