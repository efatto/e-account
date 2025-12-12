# Copyright 2025 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR timesheet project constraint",
    "version": "14.0.1.0.0",
    "category": "Timesheet",
    "license": "AGPL-3",
    "author": "Sergio Corato",
    "website": "https://github.com/efatto/e-account",
    "summary": "Limit project selectable in account analytic line and add a constraint",
    "depends": [
        "hr_timesheet",
    ],
    "data": [
        "views/hr_timesheet.xml",
    ],
    "installable": True,
    # "pre_init_hook": "pre_init_hook",
}
