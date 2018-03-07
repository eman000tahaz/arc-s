# -*- coding: utf-8 -*-

from odoo.report import report_sxw
from odoo import models, api

class report_tenbytenant(models.AbstractModel):
	_name = 'report.realestate.report_tenancy_by_tenant'

	def get_details(self, start_date, end_date, tenant_id):
		tenancy_obj = self.env['account.analytic.account']
		tenancy_ids = tenancy_obj.search([('tenant_id','=',tenant_id[0]),('date_start','>=',start_date),('date_start','<=',end_date),('is_property','=',True)])
		return tenancy_ids

	@api.model
	def render_html(self, docids, data=None):
		self.model = self.env.context.get('active_model')
		docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
		start_date = data['form'].get('start_date')
		end_date = data['form'].get('end_date')
		tenant_id = data['form'].get('tenant_id')
		tenant = self.env['tenant.partner'].search([('id', '=', tenant_id[0])])
		records = self.get_details(start_date,end_date,tenant_id)

		docargs = {
			'doc_ids': self.ids,
			'doc_model': self.model,
			'data': data['form'],
			'docs': docs,
			'records': records,
			'start_date': start_date,
			'end_date':end_date,
			'tenant_name':tenant.name,
		}
		return self.env['report'].render('realestate.report_tenancy_by_tenant', docargs)
