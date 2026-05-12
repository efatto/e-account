import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """
    Esegue il fix degli XMLID prima dell'installazione del modulo.
    """
    _logger.info("Esecuzione pre-init hook per il fix degli XMLID di l10n_it")
    env["account.chart.template"]._pre_install_l10n_it_fix_xmlids()
