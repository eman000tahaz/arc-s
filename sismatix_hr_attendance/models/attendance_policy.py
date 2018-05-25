# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AttendancePolicy(models.Model):
	_name = "attendance.policy"

	name = fields.Char('Name')
	overtime_ids = fields.Many2many('hr.overtime', string="Overtime Rules")
	late_id = fields.Many2one('hr.late')
	absence_id = fields.Many2one('hr.absence')
	diff_id = fields.Many2one('hr.diff.time')