from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_section_grouping = fields.Selection(
        selection_add=[("delivery_note_sale", "Group by Delivery Note and Sale Order")],
        ondelete={"delivery_note_sale": "set default"},
    )
