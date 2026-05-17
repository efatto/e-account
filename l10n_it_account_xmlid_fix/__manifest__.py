# Copyright 2026 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Italy - Account XMLID Fix",
    "version": "18.0.1.0.0",
    "category": "Localization/Italy",
    "summary": "Fix account XMLIDs before l10n_it installation",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "depends": ["account", "l10n_it"],
    "data": [],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
    "auto_install": True,
}
