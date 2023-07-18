# Copyright 2023 Sergio Corato
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    table = "account_invoice_dueamount_line"
    column = "invoice_id"
    if openupgrade.column_exists(env.cr, "account_move", "old_invoice_id"):
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """UPDATE {0} t
            SET {1} = m.id
            FROM account_move m
            WHERE m.old_invoice_id = t.{1}"""
            ).format(
                sql.Identifier(table),
                sql.Identifier(column),
            ),
        )
