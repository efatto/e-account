# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMailNoFollowernotification(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_obj = self.env['res.partner']
        self.partner_01 = self.env.ref('base.res_partner_2')
        self.demo_user = self.env.ref('base.user_demo')
        self.partner_03 = self.demo_user.copy().partner_id

    def test_send_email_no_follower_notification(self):
        ctx = self.env.context.copy()
        ctx.update({
            'default_model': 'res.partner',
            'default_res_id': self.partner_01.id,
            'default_composition_mode': 'comment',
        })
        mail_compose = self.env['mail.compose.message']
        self.partner_01.message_subscribe(
            partner_ids=[self.demo_user.partner_id.id])
        values = mail_compose.with_context(ctx)\
            .onchange_template_id(False, 'comment', 'res.partner',
                                  self.partner_01.id)['value']
        values['partner_ids'] = [(4, self.demo_user.partner_id.id),
                                 (4, self.partner_03.id)]
        compose_id = mail_compose.with_context(ctx).create(values)
        compose_id.with_context(ctx).send_mail()
        res = self.env["mail.message"].search(
            [('model', '=', 'res.partner'),
             ('res_id', '=', self.partner_01.id)])
        self.assertEqual(len(res.ids), 1)
        message = self.env['mail.message']
        # check all followers are notified (as not removed from partner_ids from user)
        for record in res:
            for notification in record.notification_ids:
                if notification.res_partner_id in (
                        self.partner_03 | self.demo_user.partner_id):
                    message += record
        self.assertEqual(len(message.ids), 2)
        values['partner_ids'] = [(6, 0, [self.partner_03.id])]
        compose_id = mail_compose.with_context(ctx).create(values)
        compose_id.with_context(ctx).send_mail()
        # search only new messages
        res = self.env["mail.message"].search(
            [('model', '=', 'res.partner'),
             ('res_id', '=', self.partner_01.id),
             ('id', 'not in', res.ids)])  # noqa
        message = self.env['mail.message']
        # check only 1 followers is notified (as 1 removed from partner_ids from user)
        for record in res:
            for notification in record.notification_ids:
                if notification.res_partner_id in (
                        self.partner_03 | self.demo_user.partner_id):
                    message += record
        self.assertEqual(len(message.ids), 1)
