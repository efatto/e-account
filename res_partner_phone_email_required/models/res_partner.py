# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, exceptions, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        if not vals.get('phone', False) and not vals.get('email', False) \
                and not vals.get('mobile', False):
            raise exceptions.ValidationError(
                _('Phone or email are required.'))
        return super(ResPartner, self).create(vals)
