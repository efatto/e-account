from openupgradelib import openupgrade
from psycopg2 import sql

from odoo import SUPERUSER_ID, api


def migrate_fields(cr):
    """
    Move data to new custom fields as they are now computed and would be deleted
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    renamed_fields = [
        (
            "net_weight",
            "net_weight_custom",
            "float",
        ),
        (
            "gross_weight",
            "gross_weight_custom",
            "float",
        ),
        (
            "volume",
            "volume_custom",
            "float",
        ),
        (
            "packages",
            "packages_custom",
            "integer",
        ),
    ]

    for fields in renamed_fields:
        # copy data
        if not openupgrade.column_exists(env.cr, "account_move", fields[1]):
            openupgrade.add_fields(
                env,
                [
                    (
                        fields[1],
                        "account.move",
                        False,
                        fields[2],
                        False,
                        "account_invoice_weight",
                    )
                ],
            )
        query = sql.SQL(
            """
            UPDATE account_move
            set {new_field} = {old_field}
            """.format(
                new_field=fields[1], old_field=fields[0]
            )
        )
        openupgrade.logged_query(
            env.cr,
            query,
        )
