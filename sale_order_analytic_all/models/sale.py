# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        order = super().create(vals)
        if not order.analytic_account_id:
            order._create_analytic_account()
        if not order.project_id:
            # use sudo() as user may not have permission to create the project
            order.sudo().with_company(order.company_id.id)._create_project()
        if not order.procurement_group_id:
            group_id = self.env["procurement.group"].create(
                {
                    "name": order.name,
                    "move_type": order.picking_policy,
                    "sale_id": order.id,
                    "partner_id": order.partner_shipping_id.id,
                }
            )
            order.procurement_group_id = group_id
        return order

    def _create_project(self):
        for sale in self:
            account = sale.analytic_account_id
            values = {
                "name": "%s - %s" % (sale.client_order_ref, sale.name)
                if sale.client_order_ref
                else sale.name,
                "allow_timesheets": True,
                "analytic_account_id": account.id,
                "partner_id": sale.partner_id.id,
                "sale_order_id": sale.id,
                "active": True,
            }
            project = self.env["project.project"].create(values)
            sale.project_id = project


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_service_generation(self):
        """Assign created project to sale order line."""
        so_lines = self.filtered(
            lambda sol: (
                sol.order_id.project_id
                and sol.is_service
                and sol.product_id.service_tracking == "task_in_project"
            )
        )
        for so_line in so_lines:
            project = so_line.order_id.project_id
            if not project.sale_line_id:
                # assign first sale line to project
                project.sale_line_id = so_line
            so_line.project_id = project
        return super()._timesheet_service_generation()
