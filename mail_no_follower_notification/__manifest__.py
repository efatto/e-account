# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mail do not notify by default",
    "summary": "Set to default to do not notify followers on mail.compose.message "
    "and add them to recipient of the mail.",
    "author": "ACSONE SA/NV," "Odoo Community Association (OCA)," "Sergio Corato",
    "website": "https://github.com/sergiocorato/e-account",
    "category": "Social Network",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mail_optional_follower_notification",
    ],
    "data": [
        "wizard/mail_compose_message_view.xml",
    ],
}
