import logging

_logger = logging.getLogger(__name__)


def create_cashflow_lines(env):
    sales = env["sale.order"].search([], order="id")
    i_max = len(sales)
    i = 0
    for sale in sales:
        i += 1
        sale.order_line._refresh_cashflow_line()
        _logger.info(f"Creating cashflow line for sale order #{i}/{i_max}")
