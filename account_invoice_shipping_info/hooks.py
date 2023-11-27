#  Copyright 2021 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql

from odoo import SUPERUSER_ID, api


def migrate_old_module(cr, registry):
    """
    Move data and fields
    from italian old module l10n_it_ddt
    to this module, adapted to new module l10n_it_delivery_note
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    renamed_fields = [
        (
            "account.move",
            "account_move",
            "weight",
            "net_weight",
        ),
        (
            "account.move",
            "account_move",
            "weight_manual_uom_id",
            "net_weight_uom_id",
        ),
        (
            "account.move",
            "account_move",
            "carriage_condition_id",
            "transport_condition_id",
        ),
        (
            "account.move",
            "account_move",
            "goods_description_id",
            "goods_appearance_id",
        ),
        (
            "account.move",
            "account_move",
            "transportation_reason_id",
            "transport_reason_id",
        ),
        (
            "account.move",
            "account_move",
            "transportation_method_id",
            "transport_method_id",
        ),
        (
            "account.move",
            "account_move",
            "ddt_date_start",
            "transport_datetime",
        ),
        (
            "account.move",
            "account_move",
            "parcels",
            "packages",
        ),
    ]

    for fields in renamed_fields:
        # copy data from account.invoice to account.move
        query = sql.SQL(
            """
UPDATE account_move
set {new_field} = ai.{old_field}
FROM account_move am
JOIN account_invoice ai ON ai.id = am.old_invoice_id
""".format(new_field=fields[3], old_field=fields[2])
        )
        openupgrade.logged_query(
            env.cr,
            query,
        )

    openupgrade.rename_fields(
        env,
        renamed_fields,
    )
