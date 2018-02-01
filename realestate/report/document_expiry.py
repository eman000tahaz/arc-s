# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models

class document_expiry(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(document_expiry, self).__init__(cr, uid, name, context=context)  
		self.localcontext.update({'get_details': self.get_details}) 
		self.context = context

	def get_details(self, start_date, end_date):
		certificate_obj = self.pool.get("property.attachment")
		certificate_ids = certificate_obj.search(self.cr, self.uid, [('expiry_date','>=',start_date),('expiry_date','<=',end_date)])
		return certificate_obj.browse(self.cr, self.uid, certificate_ids)

class report_docexpire(models.AbstractModel):
	_name = 'report.realestate.report_document_expiry'
	_inherit = 'report.abstract_report'
	_template = 'realestate.report_document_expiry'
	_wrapped_report_class = document_expiry

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: