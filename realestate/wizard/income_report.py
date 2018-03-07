# -*- coding: utf-8 -*-

from odoo import models, fields, api


class income_report(models.TransientModel):

	_name = 'income.report'

	start_date = fields.Date('Start date', required=True)
	end_date = fields.Date('End date', required=True)

	@api.multi
	def print_report(self):
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['start_date', 'end_date'])[0]
		records = self.env[data['model']].browse(data.get('ids', []))
		return self.env['report'].get_action(records, 'realestate.report_income_expenditure', data=data)
