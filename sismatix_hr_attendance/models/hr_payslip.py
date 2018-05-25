# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'


    attendance_sheet_id = fields.Many2one('attendance.sheet', string="Attendance Sheet")
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)



    @api.onchange('employee_id')
    def get_attendance_sheet_domain(self):
    	if self.employee_id:
    		domain = [('employee_id', '=', self.employee_id.id)]
    		return {
				'domain':{
					'attendance_sheet_id': domain,
					}
				}

	@api.onchange('attendance_sheet_id')
	def get_form_details(self):
		if self.attendance_sheet_id:
			return {
				'default':{
					'date_from': self.attendance_sheet_id.date_from,
					'date_to': self.attendance_sheet_id.date_to,
					}
				}