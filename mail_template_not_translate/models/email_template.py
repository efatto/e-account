# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class EmailTemplate(models.Model):
    _inherit = "email.template"

    body_html = fields.Html(translate=False)
