# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mail no autofollow",
    "summary": """
        Set default no autofollow and remove option to choose if you want to
        automatically add new recipients as followers on mail.compose.message""",
    "author": "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "category": "Social Network",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mail",
    ],
    "data": [],
    "excludes": ["mail_optional_autofollow"],
    "installable": True,
}
