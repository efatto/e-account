# Copyright 2024 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Temporary module to migrate from l10n_it_edi to l10n_it_fatturapa",
    "version": "14.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "summary": "This module will prepare fields to be used by Italian "
    "FatturaPA modules.",
    "website": "https://github.com/sergiocorato/e-account",
    "license": "AGPL-3",
    "depends": [
        "account",
        "l10n_it_account_tax_kind",
        "l10n_it_rea",
        "l10n_it_vat_payability",
    ],
    "data": [],
    "installable": True,
    "post_init_hook": "migrate_fields",
}
