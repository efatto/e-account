from odoo import api, models


class CommentTemplate(models.AbstractModel):
    _inherit = "comment.template"
    _comment_template_partner_field_name = "partner_id"

    @api.depends(_comment_template_partner_field_name)
    def _compute_comment_template_ids(self):
        for record in self:
            current_comment_template_ids = record.comment_template_ids
            super(CommentTemplate, record)._compute_comment_template_ids()
            if current_comment_template_ids and not record.comment_template_ids:
                record.comment_template_ids = current_comment_template_ids
