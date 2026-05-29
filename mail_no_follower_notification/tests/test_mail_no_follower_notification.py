from odoo.tests import Form

from odoo.addons.mail.tests.test_mail_composer import TestMailComposer


class TestMailNoFollowernotification(TestMailComposer):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.partner_01 = cls.env.ref("base.res_partner_2")
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.partner_03 = cls.demo_user.copy().partner_id
        return res

    def _test_send_email(self, remove_followers=None):
        followers = self.demo_user.partner_id | self.partner_03
        self.partner_01.message_subscribe(
            partner_ids=followers.ids,
        )
        form = Form(
            self.env["mail.compose.message"].with_context(
                default_partner_ids=followers.ids,
                default_model=self.partner_01._name,
                default_res_ids=self.partner_01.ids,
                default_composition_mode="comment",
                test_optional_follow_notification=True,
            ),
            view=self.env.ref("mail.email_compose_message_wizard_form"),
        )
        form.body = "<p>Hello</p>"
        self.assertEqual(len(form.partner_ids.ids), 2)
        self.assertEqual(
            sorted(form.partner_ids.ids),
            sorted(followers.ids),
            "Default populates the field",
        )
        if remove_followers:
            new_followers = followers - remove_followers
            form.partner_ids = new_followers
        saved_form = form.save()

        with self.mock_mail_gateway():
            result_mails_su, result_messages = saved_form._action_send_mail()
            self.assertEqual(len(result_messages.ids), 1)
            notified_partners = result_messages.mapped(
                "notification_ids.res_partner_id"
            )
            if remove_followers:
                self.assertEqual(
                    sorted(notified_partners.ids),
                    sorted(new_followers.ids),
                )
            else:
                self.assertEqual(
                    sorted(notified_partners.ids),
                    sorted(followers.ids),
                )

    def test_01_send_email(self):
        self._test_send_email()

    def test_02_send_email_removing_follower(self):
        self._test_send_email(remove_followers=self.partner_03)
