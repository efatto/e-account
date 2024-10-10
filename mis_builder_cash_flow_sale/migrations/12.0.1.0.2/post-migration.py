# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # force cashflow line refresh
    sales = env['sale.order'].search([
        ('invoice_status', '!=', 'invoiced'),
    ], order="id")
    i_max = len(sales)
    i = 0
    for sale in sales:
        i += 1
        sale.order_line._refresh_cashflow_line()
        _logger.info("Creating cashflow line for sale order #%s/%s" % (i, i_max))
