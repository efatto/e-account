from odoo import _, api, models
from odoo.exceptions import UserError


class RibaListLine(models.Model):
    _inherit = 'riba.distinta.line'

    @api.multi
    def riba_line_unsettlement(self):
        for riba_line in self:
            if not riba_line.distinta_id.config_id.settlement_journal_id:
                raise UserError(_('Please define a Settlement Journal.'))

            move_line_model = self.env['account.move.line']

            settlement_move_line = move_line_model.search([
                ('account_id', '=', riba_line.acceptance_account_id.id),
                ('move_id', '=', riba_line.acceptance_move_id.id),
                ('debit', '!=', 0)
                ])

            settlement_move_amount = settlement_move_line.debit

            settlement_move_line_credit = move_line_model.search([
                ('move_id.journal_id', '=', riba_line.distinta_id.config_id.
                 settlement_journal_id.id),
                ('partner_id', '=', riba_line.partner_id.id),
                ('account_id', '=', riba_line.acceptance_account_id.id),
                ('credit', '=', settlement_move_amount),
            ])
            settlement_move = settlement_move_line_credit.move_id
            settlement_move.line_ids.remove_move_reconcile()
            settlement_move.button_cancel()
            settlement_move.sudo().unlink()
            riba_line.write({'state': 'accredited'})
