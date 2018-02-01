# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tenancy_property_report(models.TransientModel):

	_name = 'tenancy.property.report'

	start_date = fields.Date('Start date', required=True)
	end_date = fields.Date('End date', required=True)
	property_id = fields.Many2one('account.asset.asset','Property', required=True)

	@api.multi
	def open_tenancy_by_property_gantt(self):
		for data_rec in self:
			data = data_rec.read([])[0]
			start_date = data['start_date']
			end_date = data['end_date']
			property_id = data['property_id'][0]
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'view_analytic_gantt')[1]
			tenancy_ids = self.env['account.analytic.account'].search([('property_id','=',property_id),('date_start','>=',start_date),('date_start','<=',end_date)])
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
	def open_tenancy_by_property_tree(self):
		for data_rec in self:
			data = data_rec.read([])[0]
			start_date = data['start_date']
			end_date = data['end_date']
			property_id = data['property_id'][0]
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_analytic_view_tree')[1]
			tenancy_ids = self.env['account.analytic.account'].search([('property_id','=',property_id),('date_start','>=',start_date),('date_start','<=',end_date)])
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
		partner_obj = self.env['account.asset.asset']
		if self._context is None:
			self._context = {}
		for data_rec in self:
			data = data_rec.read([])[0]
			partner_rec = partner_obj.browse(data['property_id'][0])
			data.update({'property_name' : partner_rec.name})
		data = {
			'ids': self.ids,
			'model': 'account.asset.asset',
			'form': data
		}
		return self.env['report'].get_action(self, 'realestate.report_tenancy_by_property',
											 data=data)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
