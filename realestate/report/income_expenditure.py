# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models

class income_expenditure(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(income_expenditure, self).__init__(cr, uid, name, context=context)  
		self.total_in = 0.00
		self.total_ex = 0.00
		self.total_gr = 0.00
		self.localcontext.update({'get_details': self.get_details, 'get_income_total' : self.get_income_total, 'get_expence_total' : self.get_expence_total, 'get_grand_total' : self.get_grand_total}) 
		self.context = context

	def get_details(self, start_date, end_date):
		report_rec = []
		property_obj = self.pool.get('account.asset.asset')
		maintenance_obj = self.pool.get("property.maintenance")
		income_obj = self.pool.get("tenancy.rent.schedule")
		property_ids = property_obj.search(self.cr, self.uid, [])
		if property_ids:
			for property_id in property_obj.browse(self.cr, self.uid, property_ids):
				tenancy_ids = []
				if property_id.tenancy_property_ids and property_id.tenancy_property_ids.ids:
					tenancy_ids += property_id.tenancy_property_ids.ids
				income_ids = income_obj.search(self.cr, self.uid, [('start_date','>=',start_date),('start_date','<=',end_date),('tenancy_id','in',tenancy_ids)])
				maintenance_ids = maintenance_obj.search(self.cr, self.uid, [('date','>=',start_date),('date','<=',end_date),('property_id','=',property_id.id)])
				total_income = 0.00
				total_expence = 0.00
				if income_ids:
					for income_id in income_obj.browse(self.cr, self.uid, income_ids):
						total_income += income_id.amount
				if maintenance_ids:
					for expence_id in maintenance_obj.browse(self.cr, self.uid, maintenance_ids):
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

class report_incom_expen(models.AbstractModel):
	_name = 'report.realestate.report_income_expenditure'
	_inherit = 'report.abstract_report'
	_template = 'realestate.report_income_expenditure'
	_wrapped_report_class = income_expenditure


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: