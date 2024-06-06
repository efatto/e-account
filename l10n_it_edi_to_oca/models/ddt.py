# from odoo import fields, models
#
#
# class L10nItDdt(models.Model):
#     _name = 'l10n_it.ddt'
#     _description = 'Transport Document'
#
#     invoice_id = fields.One2many(
#         'account.move', 'l10n_it_ddt_id', string='Invoice Reference')
#     name = fields.Char(
#         string="Numero DDT", size=20, help="Transport document number", required=True)
#     date = fields.Date(
#         string="Data DDT", help="Transport document date", required=True)
