from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """The custom fields are renamed to match the shipping fields of
    ``l10n_it_accompanying_invoice`` they store manual values for.
    """
    openupgrade.rename_fields(
        env,
        [
            (
                "account.move",
                "account_move",
                "net_weight_custom",
                "delivery_net_weight_custom",
            ),
            (
                "account.move",
                "account_move",
                "gross_weight_custom",
                "delivery_gross_weight_custom",
            ),
            (
                "account.move",
                "account_move",
                "volume_custom",
                "delivery_volume_custom",
            ),
            (
                "account.move",
                "account_move",
                "packages_custom",
                "delivery_packages_custom",
            ),
        ],
    )
