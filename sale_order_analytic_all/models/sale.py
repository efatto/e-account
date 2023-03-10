# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if not order.analytic_account_id:
            order._create_analytic_account()
        if not order.project_id:
            order._create_project()
        if not order.procurement_group_id:
            group_id = self.env['procurement.group'].create({
                'name': order.name,
                'move_type': order.picking_policy,
                'sale_id': order.id,
                'partner_id': order.partner_shipping_id.id,
            })
            order.procurement_group_id = group_id
        return order

    @api.multi
    def _create_project(self):
        self.ensure_one()
        account = self.analytic_account_id
        values = {
            'name': '%s - %s' % (
                self.client_order_ref, self.name
            ) if self.client_order_ref else self.name,
            'allow_timesheets': True,
            'analytic_account_id': account.id,
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'active': True,
        }
        project = self.env['project.project'].create(values)
        self.project_id = project


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_service_generation(self):
        """Handle task creation with sales order's project."""
        so_lines = self.filtered(lambda sol: (
            sol.order_id.project_id and
            sol.is_service and
            sol.product_id.service_tracking == 'task_new_project'))
        for so_line in so_lines:
            project = so_line.order_id.project_id
            if not project.sale_line_id:
                # assign first sale line to project
                project.sale_line_id = so_line
            so_line.project_id = project
            so_line._timesheet_create_task(project=project)
        return super()._timesheet_service_generation()
