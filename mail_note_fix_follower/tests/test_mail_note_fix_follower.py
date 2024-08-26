
from odoo.tests.common import SavepointCase


class TestMailNoteFixFollower(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.partner_01 = cls.env.ref("base.res_partner_2")
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.partner_03 = cls.demo_user.copy().partner_id

    def test_01_send_email(self):
        ctx = self.env.context.copy()
        ctx.update(
            {
                "default_model": "res.partner",
                "default_res_id": self.partner_01.id,
                "default_composition_mode": "comment",
                "test_optional_follow_notification": True,
            }
        )
        mail_compose = self.env["mail.compose.message"]
        self.partner_01.message_subscribe(
            partner_ids=[self.demo_user.partner_id.id, self.partner_03.id]
        )
        old_res = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.partner_01.id)]
        )
        values = mail_compose.with_context(ctx).onchange_template_id(
            False, "comment", "res.partner", self.partner_01.id
        )["value"]
        compose_id = mail_compose.with_context(ctx).create(values)
        compose_id.with_context(ctx).send_mail()
        self.assertEqual(len(compose_id.partner_ids.ids), 2)
        res = self.env["mail.message"].search(
            [
                ("model", "=", "res.partner"),
                ("res_id", "=", self.partner_01.id),
                ("id", "not in", old_res.ids),
            ]
        )  # noqa
        self.assertEqual(len(res.ids), 1)
        notified_partner = self.env["res.partner"]
        # check all followers are notified (as not removed from partner_ids from user)
        for record in res:
            for notification in record.notification_ids:
                if notification.res_partner_id in (
                    self.partner_03 | self.demo_user.partner_id
                ):
                    notified_partner |= notification.res_partner_id
        self.assertEqual(len(notified_partner.ids), 2)

    def test_02_send_email_removing_follower(self):
        ctx = self.env.context.copy()
        ctx.update(
            {
                "default_model": "res.partner",
                "default_res_id": self.partner_01.id,
                "default_composition_mode": "comment",
                "test_optional_follow_notification": True,
            }
        )
        mail_compose = self.env["mail.compose.message"]
        self.partner_01.message_subscribe(
            partner_ids=[self.demo_user.partner_id.id, self.partner_03.id]
        )
        old_res = self.env["mail.message"].search(
            [("model", "=", "res.partner"), ("res_id", "=", self.partner_01.id)]
        )
        values = mail_compose.with_context(ctx).onchange_template_id(
            False, "comment", "res.partner", self.partner_01.id
        )["value"]
        compose_id = mail_compose.with_context(ctx).create(values)
        self.assertEqual(len(compose_id.partner_ids.ids), 2)
        for partner in compose_id.partner_ids:
            self.assertIn(partner, [self.partner_03, self.demo_user.partner_id])
        compose_id.partner_ids -= self.partner_03
        self.assertEqual(len(compose_id.partner_ids.ids), 1)
        compose_id.with_context(ctx).send_mail()
        res = self.env["mail.message"].search(
            [
                ("model", "=", "res.partner"),
                ("res_id", "=", self.partner_01.id),
                ("id", "not in", old_res.ids),
            ]
        )  # noqa
        self.assertEqual(len(res.ids), 1)
        notified_partner = self.env["res.partner"]
        # check only 1 follower is notified (as 1 is removed from partner_ids from user)
        for record in res:
            for notification in record.notification_ids:
                if notification.res_partner_id in (
                    self.partner_03 | self.demo_user.partner_id
                ):
                    notified_partner |= notification.res_partner_id
        self.assertEqual(len(notified_partner.ids), 1)
