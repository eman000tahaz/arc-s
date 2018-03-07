# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tenancy_tenant_report(models.TransientModel):

	_name = 'tenancy.tenant.report'

	start_date = fields.Date('Start date', required=True)
	end_date = fields.Date('End date', required=True)
	tenant_id = fields.Many2one('tenant.partner', 'Tenant', required=True)

	@api.multi
	def open_tanancy_tenant_gantt_view(self):
		for data_rec in self:
			data = data_rec.read([])[0]
			start_date = data['start_date']
			end_date = data['end_date']
			tenant_id = data['tenant_id'][0]
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'view_analytic_gantt')[1]
			tenancy_ids = self.env["account.analytic.account"].search([('tenant_id','=',tenant_id),('date_start','>=',start_date),('date_start','<=',end_date)])
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'gantt',
			'res_model': 'account.analytic.account',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context':self._context,
			'domain':[('id','in',tenancy_ids.ids)],
			}

	@api.multi
	def open_tanancy_tenant_tree_view(self):
		for data_rec in self:
			data = data_rec.read([])[0]
			start_date = data['start_date']
			end_date = data['end_date']
			tenant_id = data['tenant_id'][0]
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_analytic_view_tree')[1]
			tenancy_ids = self.env['account.analytic.account'].search([('tenant_id','=',tenant_id),('date_start','>=',start_date),('date_start','<=',end_date)])
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'tree',
			'res_model': 'account.analytic.account',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context':self._context,
			'domain':[('id','in',tenancy_ids.ids)],
			}

	@api.multi
	def print_report(self):
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['start_date', 'end_date', 'tenant_id'])[0]
		records = self.env[data['model']].browse(data.get('ids', []))
		return self.env['report'].get_action(records, 'realestate.report_tenancy_by_tenant', data=data)


