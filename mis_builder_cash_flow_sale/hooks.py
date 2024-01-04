# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def create_cashflow_lines(cr, registry):
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
        sales = env["sale.order"].search([], order="id")
        i_max = len(sales)
        i = 0
        for sale in sales:
            i += 1
            sale.order_line._refresh_cashflow_line()
            _logger.info("Creating cashflow line for sale order #%s/%s" % (i, i_max))
