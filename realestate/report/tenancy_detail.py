# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models


class tenancy_detail(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(tenancy_detail, self).__init__(cr, uid, name, context=context)  
		self.localcontext.update({'get_details': self.get_details}) 
		self.context = context

	def get_details(self, start_date, end_date, property_id):
		tenancy_obj = self.pool.get("account.analytic.account")
		tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('property_id','=',property_id[0]),('date_start','>=',start_date),('date','<=',end_date),('is_property','=',True)])
		return tenancy_obj.browse(self.cr, self.uid, tenancy_ids)


class report_tenancybyprop(models.AbstractModel):
	_name = 'report.realestate.report_tenancy_by_property'
	_inherit = 'report.abstract_report'
	_template = 'realestate.report_tenancy_by_property'
	_wrapped_report_class = tenancy_detail

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: