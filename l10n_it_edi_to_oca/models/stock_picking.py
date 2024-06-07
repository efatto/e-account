# from odoo import fields, models


# class StockPicking(models.Model):
#     _inherit = "stock.picking"
#
#     l10n_it_transport_reason = fields.Selection([
#      ('sale', 'Sale'),
#      ('outsourcing', 'Outsourcing'),
#      ('evaluation', 'Evaluation'),
#      ('gift', 'Gift'),
#      ('transfer', 'Transfer'),
#      ('substitution', 'Substitution'),
#      ('attemped_sale', 'Attempted Sale'),
#      ('loaned_use', 'Loaned for Use'),
#      ('repair', 'Repair')], default="sale", tracking=True,
#      string='Transport Reason')
#     l10n_it_transport_method = fields.Selection(
#     [('sender', 'Sender'), ('recipient', 'Recipient'),
#     ('courier', 'Courier service')],
#       default="sender", string='Transport Method')
#     l10n_it_transport_method_details = fields.Char('Transport Note')
#     l10n_it_parcels = fields.Integer(string="Parcels", default=1)
#     l10n_it_country_code = fields.Char(related="company_id.country_id.code")
#     l10n_it_ddt_number = fields.Char('DDT Number', readonly=True)
#     l10n_it_show_print_ddt_button = fields.Boolean(
#     compute="_compute_l10n_it_show_print_ddt_button")

#
# class StockPickingType(models.Model):
#     _inherit = 'stock.picking.type'
#
#     l10n_it_ddt_sequence_id = fields.Many2one('ir.sequence')
