# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import dateutil.parser
import datetime
#import calendar

class AttendanceSheet(models.Model):
	_name = "attendance.sheet"

	employee_id = fields.Many2one('hr.employee', string='Employee')
	date_from = fields.Date()
	date_to = fields.Date()
	name = fields.Char('Name')
	policy_id = fields.Many2one('attendance.policy', string='Attendance Policy')
	attendance_line_ids = fields.One2many('attendance.line', 'attendance_sheet_id')
	state = fields.Selection([('draft', 'Draft'), ('calc', 'Calculated'), ('confirmed', 'Confirmed'), ('approved', 'Approved')],
								default='draft')
	overtime_no = fields.Integer('No of Overtime')
	total_overtime = fields.Float('Total Overtime')
	late_no = fields.Integer('No of Late In')
	total_late = fields.Float('Total Late In')
	diff_no = fields.Integer('No of Difference Time')
	total_diff = fields.Float('Total Difference Time')
	absence_no = fields.Integer('No of Absence')
	total_absence = fields.Float('Total Absence')



	@api.onchange('employee_id')
	def get_name(self):
		if self.employee_id:
			name = str(self.employee_id.name)
			self.name = 'Attendance Sheet Of ' + name 

	@api.one
	def get_attendance(self):
		domain = [('employee_id', '=', self.employee_id.id), ('date', '>=', self.date_from), ('date', '<=', self.date_to)]
		attendances = self.env['hr.attendance'].search(domain)
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		
		overtime_no = 0
		late_no = 0
		diff_no = 0
		absence_no = 0
		total_overtime = 0
		total_late = 0
		total_diff = 0
		total_absence = 0

		for attend in attendances:
			date = attend.date
			status = ''
			note = ''
			date_year = int(date[0:4])
			date_month = int(date[5:7])
			date_day = int(date[8:10])
			day_indx = n = datetime.datetime(date_year, date_month, date_day).weekday()
			day = days[day_indx]

			public_holidays = self.env['public.holiday'].search([('date_from', '<=', date), ('date_to', '>=', date)])
			calendar = self.employee_id.calendar_id
			work_day = self.env['resource.calendar.attendance'].search([('calendar_id', '=', calendar.id), ('dayofweek', '=', day_indx), ('date_from', '<=', date), ('date_to', '>=', date)])

			if public_holidays:
				plan_sign_in = 0
				plan_sign_out = 0
				status = 'Public Holiday'
			elif work_day:
				plan_sign_in = work_day[0].hour_from
				plan_sign_out = work_day[0].hour_to
			else:
				plan_sign_in = 0
				plan_sign_out = 0

			act_sign_in = attend.check_in[11:16]
			act_sign_in_hrs = str(int(act_sign_in[0:2]) + 2)
			act_sign_in_mins = act_sign_in[3:5]
			act_sign_out = attend.check_out[11:16]
			act_sign_out_hrs = str(int(act_sign_out[0:2]) + 2)
			act_sign_out_mins = act_sign_out[3:5]

			plan_working_hours = plan_sign_out - plan_sign_in
			float_act_sign_in = float('%s.%s' % (act_sign_in_hrs, act_sign_in_mins))
			float_act_sign_out = float('%s.%s' % (act_sign_out_hrs, act_sign_out_mins))
			act_working_hours =  float_act_sign_out - float_act_sign_in


			overtime = 0
			if plan_sign_in > float_act_sign_in:
				overtime += (plan_sign_in - float_act_sign_in)
			if plan_sign_out < float_act_sign_out:
				overtime += (float_act_sign_out - plan_sign_out)
			if overtime:
				overtime_ids = self.policy_id.overtime_ids
				new_overtime = overtime
				if public_holidays:
					for overtime_rule in overtime_ids:
						if overtime_rule.type_id == 'ph' and overtime >= overtime_rule.apply_after:
							new_overtime = overtime * overtime_rule.rate
				elif work_day:
					for overtime_rule in overtime_ids:
						if overtime_rule.type_id == 'w-day' and overtime >= overtime_rule.apply_after:
							new_overtime = overtime * overtime_rule.rate
				else:
					for overtime_rule in overtime_ids:
						if overtime_rule.type_id == 'w-end' and overtime >= apply_after:
							new_overtime = overtime * overtime_rule.rate
				overtime_no += 1
				total_overtime += new_overtime


			late = 0
			if plan_sign_in != 0.0:
				if float_act_sign_in > plan_sign_in:
					late = float_act_sign_in - plan_sign_in
					late_rules = self.env['late.period'].search([('late_id', '=', self.policy_id.late_id.id)],order='time')
					new_late = late
					if late_rules:
						changed = False
						if late < late_rules[0].time:
							changed = True
						for rule in late_rules:
							if not changed:
								if late <= rule.time:
									if rule.calc_type == 'fixed':
										new_late = rule.amount
										changed = True
									elif rule.calc_type == 'rate':
										new_late = late * rule.rate
										changed = True
					late_no += 1
					total_late += new_late


			diff_time = 0
			if plan_sign_out != 0.0:
				if float_act_sign_out < plan_sign_out:
					diff_time = plan_sign_out - float_act_sign_out
					diff_rules = self.env['diff.period'].search([('diff_id', '=', self.policy_id.diff_id.id)], order='time')
					new_diff_time = diff_time
					if diff_rules:
						changed = False
						if diff_time < diff_rules[0].time:
							changed = True
						for rule in diff_rules:
							if not changed:
								if diff_time <= rule.time:
									if rule.calc_type == 'fixed':
										new_diff_time = rule.amount
										changed = True
									elif rule.calc_type == 'rate':
										new_diff_time = diff_time * rule.rate
										changed = True
					diff_no += 1
					total_diff += new_diff_time 


			if plan_working_hours:
				if not act_working_hours:
					absence_no += 1
					absence_rule = self.env['absence.time'].search([('absence_id', '=', self.policy_id.absence_id.id), ('times', '=', absence_no)])
					if absence_rule:
						absence = absence_rule[0].rate
						total_absence += absence


			attendance_line_vals = {
									'date': date,
									'day': day,
									'plan_sign_in': plan_sign_in,
									'plan_sign_out': plan_sign_out,
									'act_sign_in': float_act_sign_in,
									'act_sign_out': float_act_sign_out,
									'overtime': overtime,
									'late': late,
									'attendance_sheet_id': self.id,
								}
			self.env['attendance.line'].create(attendance_line_vals)


		return self.write({
					'state': 'calc',
					'overtime_no': overtime_no,
					'late_no': late_no,
					'diff_no': diff_no,
					'absence_no': absence_no,
					'total_overtime': total_overtime,
					'total_late': total_late,
					'total_diff': total_diff,
					'total_absence': total_absence,
					})



					# pass



	@api.one
	def to_confirm(self):
		self.write({
					'state': 'confirmed',
				})

	@api.one
	def to_approve(self):
		self.write({
					'state': 'approved',
				})

	@api.one
	def to_draft(self):
		self.write({
					'state': 'draft',
				})

class AttendanceLine(models.Model):
	_name = "attendance.line"

	date = fields.Date('Date')
	day = fields.Char('Day')
	plan_sign_in = fields.Float('Planned Sign In')
	plan_sign_out = fields.Float('Planned Sign Out')
	act_sign_in = fields.Float('Actual Sign In')
	act_sign_out = fields.Float('Actual Sign Out')
	late = fields.Float('Late In')
	overtime = fields.Float('OverTime')
	diff_time = fields.Float('Diff Time')
	status = fields.Char('Status')
	note = fields.Text('Note')
	attendance_sheet_id = fields.Many2one('attendance.sheet')
