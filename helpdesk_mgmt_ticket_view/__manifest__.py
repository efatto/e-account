# Copyright 2025 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Show entire helpdesk ticket name in portal",
    "version": "18.0.1.0.0",
    "category": "other",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "license": "AGPL-3",
    "depends": [
        "helpdesk_mgmt",
        "web",
    ],
    "assets": {
        "web.assets_backend": ["helpdesk_mgmt_ticket_view/static/src/scss/view.scss"]
    },
    "installable": True,
}
