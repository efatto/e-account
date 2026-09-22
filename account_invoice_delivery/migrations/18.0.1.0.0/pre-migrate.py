from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [("account.move", "account_move", "delivery_carrier_id", "delivery_method_id")],
    )
