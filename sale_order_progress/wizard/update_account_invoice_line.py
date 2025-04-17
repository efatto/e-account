from odoo import fields, models


class UpdateAccountInvoiceLineWizard(models.TransientModel):
    _name = "wizard.update.account.invoice.line"
    _description = "Wizard update account invoice line"

    sal_id = fields.Many2one(comodel_name="sale.order.progress", required=True)
    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Sale Orders",
        default=lambda self: self.env["account.invoice.line"].browse(
            self.env.context.get("active_id")).sale_order_ids,
    )

    def update_account_invoice_line(self):
        rec_ids = self.env.context.get("active_ids", False)
        records = self.env[self.env.context["active_model"]].browse(rec_ids)
        for rec in records:
            rec.write(
                {
                    "sale_order_progress_id": self.sal_id.id,
                }
            )
