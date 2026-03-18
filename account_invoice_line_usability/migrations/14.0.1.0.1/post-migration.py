from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Recompute move_price_unit and move_price_total fields for invoices
    for inv in env["account.move"].search([
        ("move_type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"])
    ]):
        for invoice_line in inv.invoice_line_ids:
            invoice_line._compute_move_price_unit()
