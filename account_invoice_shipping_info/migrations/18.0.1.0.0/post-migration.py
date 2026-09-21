from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Copy values to new fields
    renamed_fields = [
        ("transport_condition_id", "delivery_transport_condition_id"),
        ("goods_appearance_id", "delivery_goods_appearance_id"),
        ("transport_reason_id", "delivery_transport_reason_id"),
        ("transport_method_id", "delivery_transport_method_id"),
        ("carrier_id", "delivery_carrier_id"),
        ("volume", "delivery_volume"),
        ("volume_uom_id", "delivery_volume_uom_id"),
        ("net_weight", "delivery_net_weight"),
        ("net_weight_uom_id", "delivery_net_weight_uom_id"),
        ("gross_weight", "delivery_gross_weight"),
        ("gross_weight_uom_id", "delivery_gross_weight_uom_id"),
        ("packages", "delivery_packages"),
        ("delivery_transport_datetime", "transport_datetime"),
    ]

    for old_column, new_column in renamed_fields:
        # copy data from account.invoice to account.move
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE account_move
            set {new_column} = {old_column}
            """,
        )
