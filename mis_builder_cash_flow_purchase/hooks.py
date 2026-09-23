import logging

_logger = logging.getLogger(__name__)


def create_cashflow_lines(env):
    purchases = env["purchase.order"].search([], order="id")
    i_max = len(purchases)
    i = 0
    for purchase in purchases:
        i += 1
        purchase.order_line._refresh_cashflow_line()
        _logger.info(f"Creating cashflow line for purchase order #{i}/{i_max}")
