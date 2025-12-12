import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("Ensure project has the same analytic account of the analytic line")
    cr.execute(
        """
        UPDATE account_analytic_line aal SET account_id = p.analytic_account_id
        LEFT JOIN project_project p ON p.id = aal.project_id
        WHERE aal.project_id IS NOT NULL
        AND p.analytic_account_id IS NOT NULL
        AND aal.account_id != p.analytic_account_id
        """
    )
