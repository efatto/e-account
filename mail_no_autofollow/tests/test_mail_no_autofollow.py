from odoo.tests import Form

from odoo.addons.mail.tests.test_mail_composer import TestMailComposer


class TestMailNoAutofollow(TestMailComposer):
    def setUp(self):
        super().setUp()
        self.partner_obj = self.env["res.partner"]
        self.partner_01 = self.env.ref("base.res_partner_10")
        self.partner_02 = self.env.ref("base.res_partner_address_17")

    def test_send_email_attachment(self):
        form = Form(
            self.env["mail.compose.message"].with_context(
                default_partner_ids=(self.partner_01 | self.partner_02).ids,
                default_model=self.partner_01._name,
                default_res_ids=self.partner_01.ids,
                default_composition_mode="comment",
                test_optional_follow_notification=True,
            ),
            view=self.env.ref("mail.email_compose_message_wizard_form"),
        )
        form.body = "<p>Hello</p>"
        saved_form = form.save()
        with self.mock_mail_gateway():
            result_mails_su, result_messages = saved_form._action_send_mail()
            self.assertEqual(len(result_messages.ids), 1)
        res = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", self.partner_01.id),
                ("partner_id", "=", self.partner_02.id),
            ]
        )
        # I check if the recipient isn't a follower
        self.assertEqual(len(res.ids), 0)
