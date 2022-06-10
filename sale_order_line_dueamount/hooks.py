# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.api import Environment
from odoo import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def create_dueamount(cr, registry):
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
        sales = env['sale.order'].search([], order="id")
        i_max = len(sales)
        i = 0
        for sale in sales:
            i += 1
            for line in sale.order_line:
                line._refresh_dueamount()
            _logger.info('Update sale order %s/%s' % (
                i, i_max
            ))
