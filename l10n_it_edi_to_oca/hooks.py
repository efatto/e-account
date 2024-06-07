from odoo import SUPERUSER_ID, api


def migrate_fields(cr, registry):  # noqa C901
    env = api.Environment(cr, SUPERUSER_ID, {})
    # compatibility with module partner_firstname
    partner_obj = env["res.partner"]
    for partner in partner_obj.search(["|", ("name", "=", False), ("name", "=", "")]):
        partner.name = " - ".join(["Nome non impostato", partner.display_name])
    # dict with current state: new state
    fatturapa_state = {
        "new": "ready",
        "other": "error",
        "to_send": "ready",
        "sent": "sent",
        "invalid": "error",
        "delivered": "delivered",
        "delivered_accepted": "accepted",
        "delivered_refused": "error",
        "delivered_expired": "accepted",
        "failed_delivery": "error",
    }
    move_obj = env["account.move"]
    if hasattr(move_obj, "l10n_it_send_state"):
        for invoice in move_obj.search([("l10n_it_send_state", "!=", False)]):
            invoice.fatturapa_state = fatturapa_state[invoice.l10n_it_send_state]

    # set tax stamp
    if hasattr(move_obj, "l10n_it_stamp_duty"):
        for invoice in move_obj.search([("l10n_it_stamp_duty", "!=", 0)]):
            invoice.manually_apply_tax_stamp = True

    # move ddt to delivery note

    # create "fatturapa.attachment.out" from 'ir.attachment'

    # set fatturapa pec server
    fetchmail_obj = env["fetchmail.server"]
    if hasattr(fetchmail_obj, "l10n_it_is_pec"):
        for fetchmail in fetchmail_obj.search([("l10n_it_is_pec", "=", True)]):
            fetchmail.is_fatturapa_pec = True

    # set partner fields
    if hasattr(partner_obj, "l10n_it_pec_email"):
        for partner in partner_obj.search([("l10n_it_pec_email", "!=", False)]):
            partner.pec_destinatario = partner.l10n_it_pec_email
            partner.electronic_invoice_subjected = True
            partner.electronic_invoice_obliged_subject = True
        for partner in partner_obj.search([("l10n_it_codice_fiscale", "!=", False)]):
            partner.fiscalcode = partner.l10n_it_codice_fiscale
        for partner in partner_obj.search([("l10n_it_pa_index", "!=", False)]):
            if len(partner.l10n_it_pa_index) == 7:
                partner.codice_destinatario = partner.l10n_it_pa_index
            else:
                partner.pa_partner_code = partner.l10n_it_pa_index
            partner.electronic_invoice_subjected = True
            partner.electronic_invoice_obliged_subject = True
    # set partner rea fields
    if hasattr(partner_obj, "l10n_it_eco_index_office"):
        for partner in partner_obj.search([("l10n_it_eco_index_office", "!=", False)]):
            partner.rea_office = partner.l10n_it_eco_index_office
        for partner in partner_obj.search([("l10n_it_eco_index_number", "!=", False)]):
            partner.rea_code = partner.l10n_it_eco_index_number
        for partner in partner_obj.search(
            [("l10n_it_eco_index_share_capital", "!=", 0)]
        ):
            partner.rea_capital = partner.l10n_it_eco_index_share_capital
        for partner in partner_obj.search(
            [("l10n_it_eco_index_sole_shareholder", "in", ["SU", "SM"])]
        ):
            partner.rea_member_type = partner.l10n_it_eco_index_sole_shareholder
        for partner in partner_obj.search(
            [("l10n_it_eco_index_liquidation_state", "!=", False)]
        ):
            partner.rea_liquidation_state = partner.l10n_it_eco_index_liquidation_state

    company_obj = env["res.company"]
    if hasattr(company_obj, "l10n_it_tax_system"):
        for company in company_obj.search([("l10n_it_tax_system", "!=", False)]):
            company.fatturapa_fiscal_position_code = company.l10n_it_tax_system
    # TODO possible improvement:
    #  at l10n_it_fatturapa installation assign fatturapa_fiscal_position_id
    #  searching by
    #  env["fatturapa.fiscal_position"].search([
    #       ("code", "=", company.fatturapa_fiscal_position_code)])

    tax_obj = env["account.tax"]
    if hasattr(tax_obj, "l10n_it_law_reference"):
        for tax in tax_obj.search([("l10n_it_law_reference", "!=", False)]):
            tax.law_reference = tax.l10n_it_law_reference
        for tax in tax_obj.search([("l10n_it_kind_exoneration", "!=", False)]):
            kind = env["account.tax.kind"].search(
                [("code", "=", tax.l10n_it_kind_exoneration)]
            )
            if kind:
                tax.kind_id = kind
        for tax in tax_obj.search([]):
            tax.payability = tax.l10n_it_vat_due_date
