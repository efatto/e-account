from odoo import fields, models


class RibaList(models.Model):
    _inherit = "riba.distinta"

    def _compute_accreditation_move_ids(self):
        self.ensure_one()
        move_ids = self.env["account.move"]
        for line in self.line_ids:
            move_ids |= line.accreditation_move_id
        self.accreditation_move_ids = move_ids

    def _get_accrual_move_ids(self):
        self.ensure_one()
        move_ids = self.env["account.move"]
        for line in self.line_ids:
            move_ids |= line.accrual_move_id
        self.accrual_move_ids = move_ids

    def riba_cancel(self):
        res = super().riba_cancel()
        for riba_list in self:
            for line in riba_list.line_ids:
                if line.accreditation_move_id:
                    line.accreditation_move_id.unlink()
        return res

    def confirm(self):
        res = super().confirm()
        for distinta in self:
            distinta.date_accepted = (
                distinta.date_accepted or fields.Date.context_today(distinta)
            )
        return res

    def settle_all_line(self):
        res = super().settle_all_line()
        for distinta in self:
            distinta.date_accreditation = (
                distinta.date_accreditation or fields.Date.context_today(distinta)
            )
        return res

    accreditation_move_ids = fields.Many2many(
        "account.move",
        compute="_compute_accreditation_move_ids",
        string="Accreditation Entries",
    )
    accrual_move_ids = fields.Many2many(
        "account.move",
        compute=_get_accrual_move_ids,
        string="Accrual Entries",
    )
    state = fields.Selection(selection_add=[("accrued", "Accrued")])


class RibaListLine(models.Model):
    _inherit = "riba.distinta.line"

    accreditation_move_id = fields.Many2one(
        "account.move", string="Accreditation Entry", readonly=True
    )
    accrual_move_id = fields.Many2one(
        "account.move",
        string="Accrual Entry",
        readonly=True,
    )
    state = fields.Selection(selection_add=[("accrued", "Accrued")])
