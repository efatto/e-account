from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Copy values to new fields
    renamed_fields = [
        ("ddt_supplier_number", "dn_supplier_number"),
        ("ddt_supplier_date", "dn_supplier_date"),
    ]

    for old_column, new_column in renamed_fields:
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE stock_picking
            SET {new_column} = {old_column}
            WHERE {old_column} IS NOT NULL
            """,
        )
