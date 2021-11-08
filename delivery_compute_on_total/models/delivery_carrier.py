# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    is_on_total = fields.Boolean(
        'Computed on Total', help="Determines whether the computation is on "
        " the total of the document.")
