# Copyright 2017-2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'ITA - Ricevute bancarie smarca pagamento',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Annulla l\'effetto del bottone marca come pagata',
    'author': 'Sergio Corato',
    'website': 'https://efatto.it',
    'license': 'AGPL-3',
    'depends': [
        'l10n_it_ricevute_bancarie',
    ],
    'data': [
        'views/riba_view.xml',
    ],
    'installable': True
}
