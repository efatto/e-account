# -*- coding: utf-8 -*-
# Copyright 2019 Sergio Corato <https://github.com/sergiocorato>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import logging
from psycopg2 import IntegrityError
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

xmlids_to_rename = [
    ("sale_order_line_dates.sale_order_requested_date_form_view",
     "sale_order_line_date.sale_order_requested_date_form_view"),
    ("sale_order_line_dates.sale_order_line_ext_tree_view",
     "sale_order_line_date.sale_order_line_ext_tree_view"),
]


def migrate(cr, version):
    """Change installed dependency name."""
    try:
        with cr.savepoint():
            cr.execute(
                """UPDATE ir_module_module set state = 'uninstalled'
                  WHERE name = 'sale_order_line_dates'""",
            )
            cr.execute(
                """UPDATE ir_module_module set state = 'installed'
                  WHERE name = 'sale_order_line_date'""",
            )
        _logger.warn("Updated dependency installed module.")
    except IntegrityError:
        _logger.info("Unable to update dependency")

    openupgrade.rename_xmlids(cr, xmlids_to_rename)
