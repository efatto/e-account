from odoo.api import Environment
from odoo import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def create_cashflow_lines(cr, registry):
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
        # Create cashflow lines only for open mrp productions.
        # It's too time expensive to select here only the productions with a delay
        # of the payment term plus planned date that is included in current period, so
        # this part is implemented directly in the mrp cashflow line refresh method.
        productions = env['mrp.production'].search([
            ('state', '!=', 'cancel'),
        ], order="id")
        i_max = len(productions)
        i = 0
        for production in productions:
            i += 1
            production.move_raw_ids._refresh_cashflow_line()
            _logger.info('Creating cashflow line for production order #%s/%s' % (
                i, i_max
            ))
