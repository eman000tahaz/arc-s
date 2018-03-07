# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models, api


class report_incom_expen(models.AbstractModel):
	_name = 'report.realestate.report_income_expenditure'

	def get_details(self, start_date, end_date):
		self.total_in = 0.00
		self.total_ex = 0.00
		self.total_gr = 0.00
		report_rec = []
		property_obj = self.env['account.asset.asset']
		maintenance_obj = self.env['property.maintenance']
		income_obj = self.env['tenancy.rent.schedule']
		property_ids = property_obj.search([])
		if property_ids:
			for property_id in property_ids:
				tenancy_ids = []
				if property_id.tenancy_property_ids and property_id.tenancy_property_ids.ids:
					tenancy_ids += property_id.tenancy_property_ids.ids
				income_ids = income_obj.search([('start_date','>=',start_date),('start_date','<=',end_date),('tenancy_id','in',tenancy_ids)])
				maintenance_ids = maintenance_obj.search([('date','>=',start_date),('date','<=',end_date),('property_id','=',property_id.id)])
				total_income = 0.00
				total_expence = 0.00
				if income_ids:
					for income_id in income_ids:
						total_income += income_id.amount
				if maintenance_ids:
					for expence_id in maintenance_ids:
						total_expence += expence_id.cost
				self.total_in += total_income 
				self.total_ex += total_expence
				report_rec.append({'property' : property_id.name, 'total_income' : total_income,'total_expence' : total_expence})
		self.total_gr = self.total_in - self.total_ex
		return report_rec


	def get_income_total(self):
		return self.total_in

	def get_expence_total(self):
		return self.total_ex

	def get_grand_total(self):
		return self.total_gr

	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		start_date = data['form'].get('start_date')
		end_date = data['form'].get('end_date')
		records = self.get_details(start_date,end_date)
		income_total = self.get_income_total()
		expence_total = self.get_expence_total()
		grand_total = self.get_grand_total()

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'records': records,
			'start_date': start_date,
			'end_date':end_date,
			'income_total': income_total,
			'expence_total': expence_total,
			'grand_total': grand_total,
		}
		return self.env['report'].render('realestate.report_income_expenditure', docargs)

