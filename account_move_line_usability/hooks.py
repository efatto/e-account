import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Ensure name column is not null")
    cr.execute(
        """UPDATE account_move_line SET name = ref
        WHERE name IS NULL and ref IS NOT NULL;"""
    )
    cr.execute(
        """UPDATE account_move_line SET name = '/'
        WHERE name IS NULL and ref IS NULL;"""
    )
