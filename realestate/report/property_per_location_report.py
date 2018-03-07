# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models, api

class report_property_per_location(models.AbstractModel):

	_name = "report.realestate.report_property_per_location1"
	
	def property_location(self,state_id):
		property_obj = self.env['account.asset.asset']
		domain = [('state_id', '=', state_id[0])]
		property_ids = property_obj.search(domain)
		property_list = []
		sub_property_list = [] 
		for property_data in property_ids:
			if property_data.child_ids:
				for sub in property_data.child_ids:
					sub_property_list.append(sub.id)
					property_dict = {
							'name':property_data.name,
							'child_ids':sub.name,
							'city':sub.city,
							'state_id':property_data.state_id.name,
							'township':sub.township
							}
					property_list.append(property_dict)
			else:
				if property_data.id not in sub_property_list:
					property_dict = {
							'name':property_data.name,
							'child_ids':False,
							'city':property_data.city,
							'state_id':property_data.state_id.name,
							'township':property_data.township
							}
					property_list.append(property_dict)
		return property_list

	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		state_id = data['form'].get('state_id')
		records = self.property_location(state_id)

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'records': records,
		}
		return self.env['report'].render('realestate.report_property_per_location1', docargs)


