# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, exceptions, api, _, tools
import base64
import csv
import cStringIO
import logging
import pytz


class HrAttendanceImport(models.TransientModel):
    _name = 'hr.attendance.import'

    date = fields.Datetime(default=fields.Datetime.now())
    data = fields.Binary('File', required=True)
    name = fields.Char('Filename')
    delimeter = fields.Char('Delimeter', default=',',
                            help='Default delimeter is ","')
    hr_employee_id = fields.Many2one(
        comodel_name='hr.employee')

    @api.multi
    def action_import(self):
        """Load Product data from the CSV file."""
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]
        # check if keys exist
        if not isinstance(keys, list) or ('date' not in keys or
                                          'sign_in' not in keys or
                                          'sign_out' not in keys):
            raise exceptions.Warning(
                _("Not 'date' or 'sign_in' or 'sign_out' keys found"))
        del reader_info[0]

        hr_attendance_obj = self.env['hr.attendance']
        hr_employee_id = self.hr_employee_id
        for i in range(len(reader_info)):
            field = reader_info[i]
            values = dict(zip(keys, field))
            if not values['sign_in'] or not values['sign_out'] or not \
                    values['date']:
                continue
            tz_date_in = fields.Datetime.to_string(
                pytz.timezone(self.env.context['tz']).localize(
                    fields.Datetime.from_string(
                        values['date'] + ' ' + values['sign_in']),
                    is_dst=None).astimezone(pytz.utc))
            if hr_attendance_obj.search([
                ('employee_id', '=', hr_employee_id.id),
                ('name', '>', tz_date_in)
            ]):
                raise exceptions.ValidationError(
                    _('Employee has already attendance in dates > than '
                    'dates in this importation.')
                )

            val_in = {
                'name': tz_date_in,
                'action': 'sign_in',
                'employee_id': hr_employee_id.id,
            }
            tz_date_out = fields.Datetime.to_string(
                pytz.timezone(self.env.context['tz']).localize(
                    fields.Datetime.from_string(
                        values['date'] + ' ' + values['sign_out']),
                    is_dst=None).astimezone(pytz.utc))
            val_out = {
                'name': tz_date_out,
                'action': 'sign_out',
                'employee_id': hr_employee_id.id,
            }
            if hr_employee_id.state == 'absent':
                # first sign in, then out
                hr_attendance_obj.create(val_in)
                hr_attendance_obj.create(val_out)
            else:
                # first sign out, then sign in
                hr_attendance_obj.create(val_out)
                hr_attendance_obj.create(val_in)

            logging.getLogger('openerp.addons.hr_attendance_import').info(
                'Imported %s attendance for %s employee: sign in %s, sign '
                'out %s.' % (
                    values['date'], hr_employee_id.name, values['sign_in'],
                    values['sign_out']))
