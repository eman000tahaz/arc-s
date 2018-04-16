# -*- coding: utf-8 -*-

from odoo import models, fields, api


class property_per_location(models.TransientModel):

	_name = 'property.per.location'

	state_id = fields.Many2one("res.country.state", 'State')

	@api.multi
	def open_property_tree(self):
		for data1 in self:
			data = data1.read([])[0]
			state_id = data['state_id']
			wiz_form_id = self.env['ir.model.data'].get_object_reference('realestate', 'property_view_asset_tree')[1]
			property_ids = self.env['account.asset.asset'].search([('state_id','=',state_id[0])])
		return {
			'view_type': 'form',
			'view_id': wiz_form_id,
			'view_mode': 'tree',
			'res_model': 'account.asset.asset',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'context':self._context,
			'domain':[('id','in',property_ids.ids)],
			}


	@api.multi
	def print_report(self):
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['state_id'])[0]
		records = self.env[data['model']].browse(data.get('ids', []))
		return self.env['report'].get_action(records, 'realestate.report_property_per_location1', data=data)