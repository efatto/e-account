
import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def create_cashflow_lines(cr, registry):
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
        sales = env["sale.order"].search([
            ("order_progress_ids", "!=", False),
        ], order="id")
        i_max = len(sales)
        i = 0
        for sale in sales:
            i += 1
            sale.order_progress_ids._refresh_cashflow_line()
            _logger.info("Creating cashflow line for sale order progress #%s/%s"
                         % (i, i_max))
