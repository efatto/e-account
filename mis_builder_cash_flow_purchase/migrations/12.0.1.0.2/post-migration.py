# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # force cashflow line refresh
    purchases = env['purchase.order'].search([
        ('invoice_status', '!=', 'invoiced'),
    ], order="id")
    i_max = len(purchases)
    i = 0
    for purchase in purchases:
        i += 1
        purchase.order_line._refresh_cashflow_line()
        _logger.info('Creating cashflow line for purchase order #%s/%s' % (
            i, i_max
        ))
