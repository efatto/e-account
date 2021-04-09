# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    header_logo = fields.Binary()
    header_logo_width = fields.Float(
        string="Width of header logo (cm)",
        help="Width will be proportioned to max 19 cm",
        default=19,
    )
    header_logo_heigth = fields.Float(
        string="Height of header logo (cm)",
        help="Height will be proportioned to max 3 cm",
        default=3,
    )
    footer_logo = fields.Binary()
    footer_logo_width = fields.Float(
        string="Width of footer logo (cm)",
        help="Width will be proportioned to max 19 cm",
        default=19,
    )
    footer_logo_heigth = fields.Float(
        string="Height of footer logo (cm)",
        help="Height will be proportioned to max 2 cm",
        default=2,
    )

    @api.onchange("header_logo_heigth")
    def onchange_logo(self):
        max_width = 19
        max_height = 3
        if self.header_logo_heigth <= 0:
            self.header_logo_heigth = max_height
        if self.header_logo_width <= 0:
            self.header_logo_width = max_width

        if (
            self.header_logo_heigth > max_height
            or self.header_logo_width > max_width
        ):
            prop = (self.header_logo_width * 100.0) / (
                self.header_logo_heigth * 100.0
            )
            height = max_width / prop
            width = max_width
            if height > max_height:
                height = max_height
                width = max_height * prop
            self.header_logo_heigth = height
            self.header_logo_width = width

    @api.onchange("footer_logo_heigth")
    def onchange_logo(self):
        max_width = 19
        max_height = 2
        if self.footer_logo_heigth <= 0:
            self.footer_logo_heigth = max_height
        if self.footer_logo_width <= 0:
            self.footer_logo_width = max_width

        if (
            self.footer_logo_heigth > max_height
            or self.footer_logo_width > max_width
        ):
            prop = (self.footer_logo_width * 100.0) / (
                self.footer_logo_heigth * 100.0
            )
            height = max_width / prop
            width = max_width
            if height > max_height:
                height = max_height
                width = max_height * prop
            self.footer_logo_heigth = height
            self.footer_logo_width = width
