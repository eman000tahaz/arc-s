# -*- coding: utf-8 -*-

import time
from odoo import api, models

class ReportSismatix(models.AbstractModel):
	_name = 'report.sismatix_report.report_sismatix'

	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		model = data['form'].get('model')
		rows = data['form'].get('rows')
		fields = data['form'].get('fields')
		docs = self.env[model].browse(self.env.context.get('active_ids', []))
		report_name = model.replace(".", " ")
		no = len(fields)
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'data': data['form'],
			'docs': docs,
			'fields': fields,
			'rows':rows,
			'report_name': report_name,
			'no': no,
		}
		return self.env['report'].render('sismatix_report.report_sismatix', docargs)