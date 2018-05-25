# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class HrAttendanceInherit(models.Model):
	_inherit = "hr.attendance"

	date = fields.Date()

	@api.onchange('check_in')
	def get_date(self):
		if self.check_in:
			self.date = self.check_in[:-9] 