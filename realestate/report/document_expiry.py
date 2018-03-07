# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models, api

class report_docexpire(models.AbstractModel):
	_name = 'report.realestate.report_document_expiry'

	def get_details(self, start_date, end_date):
		certificate_obj = self.env['property.attachment']
		certificate_ids = certificate_obj.search([('expiry_date','>=',start_date),('expiry_date','<=',end_date)])
		return certificate_ids

	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		start_date = data['form'].get('start_date')
		end_date = data['form'].get('end_date')
		records = self.get_details(start_date,end_date)

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'records': records,
			'start_date': start_date,
			'end_date':end_date,
		}
		return self.env['report'].render('realestate.report_document_expiry', docargs)


