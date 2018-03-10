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
		headers_names = data['form'].get('headers_names')
		docs = self.env[model].browse(self.env.context.get('active_ids', []))
		report_name = model.replace(".", " ")
		no = len(fields)
		fields_total = []

		for field in headers_names:
			field_id = self.env['ir.model.fields'].search([('model', '=', model),
															('name', '=', field)])
			if field_id.ttype in ['integer', 'float', 'monetary']:
				field_sum = 0
				field_indx = headers_names.index(field)
				for row in rows:
					field_sum += row[field_indx]
			else:
				field_sum = " "
			fields_total.append(field_sum)
		rows.append(fields_total)

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