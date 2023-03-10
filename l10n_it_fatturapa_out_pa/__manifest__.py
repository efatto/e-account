# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Fattura elettronica - avviso per fatture PA",
    "summary": "Blocca l'invio di fatture PA se il file non è stato firmato",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Hidden",
    "website": "https://github.com/sergiocorato/e-account",
    "author": "Sergio Corato",
    "maintainers": ["sergiocorato"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "depends": [
        "l10n_it_fatturapa_out",
        "l10n_it_sdi_channel",
    ],
    "data": [
        "views/fatturapa_attachment_views.xml",
        "views/sdi_views.xml",
    ],
}
