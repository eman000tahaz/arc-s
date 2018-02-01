# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models


class property_per_location_report(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context=None):
		super(property_per_location_report, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
			'property_location' : self.property_location,
		})

	def property_location(self,data):
		property_obj = self.pool.get('account.asset.asset')
		domain = [('state_id', '=', data['state_id'][0])]
		property_ids = property_obj.search(self.cr, self.uid, domain)
		property_list = []
		sub_property_list = [] 
		for property_data in property_obj.browse(self.cr, self.uid, property_ids):
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

class report_property_per_location(models.AbstractModel):

	_name = "report.realestate.report_property_per_location1"
	_inherit = "report.abstract_report"
	_template = "realestate.report_property_per_location1"
	_wrapped_report_class = property_per_location_report
