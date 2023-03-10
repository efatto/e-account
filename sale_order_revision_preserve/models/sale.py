# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def copy_revision_with_context(self):
        default_data = self.default_get([])
        new_rev_number = max(
            self.old_revision_ids.mapped('revision_number') or [0]) + 1
        default_data.update({
            'active': False,
            'state': 'cancel',
            'revision_number': new_rev_number,
            'unrevisioned_name': self.unrevisioned_name,
            'name': self.name,
            'client_order_ref': self.client_order_ref,
        })
        self.write({
            'state': 'draft',
            # revision_number of active so is unchanged (always 0), as there is an sql
            # constraint that forbid to write the same number, even if modified later
            # 'revision_number': new_rev_number,
            'name': '%s-%02d' % (self.unrevisioned_name, new_rev_number),
        })
        new_revision = self.copy(default_data)
        self.old_revision_ids.write({
            'current_revision_id': self.id,
        })
        self.write({
            'old_revision_ids': [(4, new_revision.id)],
        })

        return new_revision

    @api.multi
    def create_revision(self):
        super().create_revision()
        return True
