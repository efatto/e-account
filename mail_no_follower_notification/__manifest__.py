# Copyright 2022 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Show recipients of email",
    "summary": "Show the recipient of the email, removing the anonimous flag "
    "'Notify followers'.",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "category": "Social Network",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mail_optional_follower_notification",
    ],
    "data": [
        "wizard/mail_compose_message_view.xml",
    ],
}
