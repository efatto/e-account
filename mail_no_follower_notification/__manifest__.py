# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mail no follower notification",
    "summary": "Never notify followers on mail.compose.message and add them on "
               "recipient of mail.",
    "author": "ACSONE SA/NV,"
              "Odoo Community Association (OCA),"
              "Sergio Corato",
    "website": "https://efatto.it",
    "category": "Social Network",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "mail",
    ],
    "data": [
        "wizard/mail_compose_message_view.xml",
    ],
}
