from datetime import timedelta

from odoo import _, fields
from odoo.tests.common import TransactionCase


class TestAccountBalanceProgressive(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.miscellaneous_journal = cls.env["account.journal"].create(
            {
                "name": "Miscellaneus journal",
                "type": "general",
                "code": "J_MISC",
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "code": "TEST.CREDIT.PROGRESSIVE",
                "name": "Credit progressive",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        cls.account_expenses = cls.env["account.account"].create(
            {
                "code": "TEST.EXPENSE.PROGRESSIVE",
                "name": "Expense progressive",
                "account_type": "expense",
            }
        )

    def create_move(self, date, debit, credit, number):
        move = self.env["account.move"].create(
            {
                "name": _("Account move # %s") % number,
                "journal_id": self.miscellaneous_journal.id,
                "date": date,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.account.id,
                            "partner_id": self.env.ref("base.res_partner_12").id,
                            "debit": debit,
                            "credit": credit,
                            "name": "Test move line",
                            "currency_id": self.ref("base.EUR"),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_expenses.id,
                            "debit": credit,
                            "credit": debit,
                            "name": "Test move line",
                            "currency_id": self.ref("base.EUR"),
                        },
                    ),
                ],
            }
        )
        return move

    def test_account_move(self):
        date = fields.Datetime.to_string(fields.Datetime.today() - timedelta(days=50))
        move = self.create_move(date, debit=50, credit=0, number=1)
        move.action_post()
        self.assertAlmostEqual(
            move.line_ids.filtered(
                lambda x: x.account_id == self.account
            ).balance_progressive,
            50,
        )
        date = fields.Datetime.to_string(fields.Datetime.today() - timedelta(days=30))
        move1 = self.create_move(date, debit=0, credit=15, number=2)
        move1.action_post()
        self.assertAlmostEqual(
            move1.line_ids.filtered(
                lambda x: x.account_id == self.account
            ).balance_progressive,
            35,
        )
        date = fields.Datetime.to_string(fields.Datetime.today())
        move2 = self.create_move(date, debit=0, credit=30, number=3)
        move2.action_post()
        self.assertAlmostEqual(
            move2.line_ids.filtered(
                lambda x: x.account_id == self.account
            ).balance_progressive,
            5,
        )
        self.assertAlmostEqual(
            move2.line_ids.filtered(
                lambda x: x.account_id == self.account_expenses
            ).balance_progressive,
            -5,
        )

    def test_multi_lines_same_date(self):
        date = fields.Date.today()
        move1 = self.create_move(date, debit=100, credit=0, number=10)
        move1.action_post()
        move2 = self.create_move(date, debit=0, credit=30, number=11)
        move2.action_post()

        line1 = move1.line_ids.filtered(lambda x: x.account_id == self.account)
        line2 = move2.line_ids.filtered(lambda x: x.account_id == self.account)

        # in the same date the progressive balance must be the same
        self.assertEqual(line1.balance_progressive, line2.balance_progressive)
