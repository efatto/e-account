# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, 'res_partner', 'company_bank_id'):
        openupgrade.convert_to_company_dependent(
            env=env,
            model_name="res.partner",
            origin_field_name="company_bank_id",
            destination_field_name="property_company_bank_id",
        )
