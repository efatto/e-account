import logging
from openupgradelib import openupgrade
from odoo import fields

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # compute days from dates
    sales = env['sale.order'].search([
        ('order_progress_ids', '!=', False),
    ], order="id")
    for sale in sales:
        for progress in sale.order_progress_ids:
            start_date = (
                progress.order_id.date_progress_end if
                progress.order_id.date_progress_end else
                progress.order_id.date_order.date()
                if progress.order_id.date_order else
                fields.Date.today()
            )
            progress.offset_days = (
                progress.date - start_date
            ).days
