from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = "date desc, credit desc, id desc"

    def _compute_balance_progressive(self):
        domain = list(self.env.context.get("domain_cumulated_balance") or [])
        query = self.env["account.move.line"]._where_calc(domain)
        # from_clause, from_params = query.from_clause
        where_clause, where_params = query.where_clause
        where_clause_params = [tuple(self.ids)] + list(where_params)

        sql = """SELECT l1.id AS line_id,
            COALESCE(SUM(l2.debit-l2.credit), 0) AS balance,
            CASE WHEN l1.currency_id <> l1.company_currency_id
                    AND l2.currency_id <> l2.company_currency_id
                    AND l1.currency_id = l2.currency_id
                THEN COALESCE(SUM(l2.amount_currency), 0)
                ELSE 0
                END
                AS balance_currency
            FROM account_move_line l1
            LEFT JOIN account_account a
            ON (a.id = l1.account_id)
            JOIN account_move m on (m.id = l1.move_id AND m.state <> 'draft')
            LEFT JOIN account_move_line l2
            ON (l1.account_id = l2.account_id
                AND (
                     l1.partner_id = l2.partner_id
                     OR
                     a.account_type not in ('asset_receivable', 'liability_payable')
                    )
               )
            AND (
                 l2.date < l1.date
                 OR (l2.date = l1.date AND l1.debit >=0)
                 OR (l2.date = l1.date AND l2.id <= l1.id)
            )
            JOIN account_move m1 on (m1.id = l2.move_id AND m1.state <> 'draft')
            WHERE l1.id IN %s """

        if where_clause:
            where_clause = "AND " + where_clause
            where_clause = where_clause.replace("account_move_line", "l1")
            sql += where_clause

        sql += (
            " GROUP BY l1.id, l1.currency_id, l1.company_currency_id,"
            " l2.currency_id, l2.company_currency_id"
        )

        self.env.cr.execute(sql, where_clause_params)
        result = self.env.cr.fetchall()

        # Inizializza tutti i record a 0
        for line in self:
            line.balance_progressive = 0
            line.balance_progressive_currency = 0

        # Aggiorna i valori per i record trovati
        if result:
            for line_id, balance, balance_currency in result:
                line = self.browse(line_id)
                line.balance_progressive = balance
                line.balance_progressive_currency = balance_currency

    balance_progressive = fields.Monetary(
        compute="_compute_balance_progressive",
        currency_field="company_currency_id",
        help="Field holding the progressive balance of the account for partner",
    )
    balance_progressive_currency = fields.Monetary(
        compute="_compute_balance_progressive",
        currency_field="currency_id",
        help="Field holding the progressive currency balance of the account for "
        "partner",
    )
