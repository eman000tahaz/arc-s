# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models


class contract_expiry(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(contract_expiry, self).__init__(cr, uid, name, context=context)  
		self.localcontext.update({'get_details': self.get_details}) 
		self.context = context

	def get_details(self, start_date, end_date):
		tenancy_obj = self.pool.get("account.analytic.account")
		tenancy_ids = tenancy_obj.search(self.cr, self.uid, [('date','>=',start_date),('date','<=',end_date),('is_property','=',True)])
		return tenancy_obj.browse(self.cr, self.uid, tenancy_ids)


class report_contexp(models.AbstractModel):
	_name = 'report.realestate.report_contract_expiry'
	_inherit = 'report.abstract_report'
	_template = 'realestate.report_contract_expiry'
	_wrapped_report_class = contract_expiry

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: