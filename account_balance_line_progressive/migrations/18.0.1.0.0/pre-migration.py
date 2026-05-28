import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Running account_balance_line_progressive pre-migration")
    ir_module_obj = env["ir.module.module"]
    ir_module_obj.update_list()
    l10n_it_module = ir_module_obj.search([("name", "=", "l10n_it")])
    _logger.info("l10n_it module is %s", l10n_it_module.state)
    module_fix = ir_module_obj.search([("name", "=", "l10n_it_account_xmlid_fix")])
    if module_fix.state == "uninstalled":
        _logger.info(
            "l10n_it_account_xmlid_fix module is uninstalled, " "attempting to install"
        )
        openupgrade.logged_query(
            env.cr,
            "UPDATE ir_module_module SET state='installed' "
            "WHERE name='l10n_it_account_xmlid_fix'",
        )
        _logger.info("l10n_it_account_xmlid_fix module set to installed")
    elif module_fix.state == "installed":
        _logger.info("l10n_it_account_xmlid_fix module already installed")
    else:
        _logger.info(
            "l10n_it_account_xmlid_fix not present or in unexpected state: %s",
            module_fix.state,
        )
