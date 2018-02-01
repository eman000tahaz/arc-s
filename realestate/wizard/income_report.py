# -*- coding: utf-8 -*-

from odoo import models, fields, api


class income_report(models.TransientModel):

	_name = 'income.report'

	start_date = fields.Date('Start date', required=True)
	end_date = fields.Date('End date', required=True)

	@api.multi
	def print_report(self):
		if self._context is None:
			self._context = {}
		data = {
			'ids': self.ids,
			'model': 'account.asset.asset',
			'form': self.read(['start_date', 'end_date'])[0]
			}
		return self.env['report'].get_action(self, 'realestate.report_income_expenditure',
											 data=data)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: