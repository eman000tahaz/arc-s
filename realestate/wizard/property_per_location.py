# -*- coding: utf-8 -*-

from odoo import models, fields, api


class property_per_location(models.TransientModel):

	_name = 'property.per.location'

	state_id = fields.Many2one("res.country.state", 'State')


	@api.multi
	def print_report(self):
		data = {}
		data['ids'] = self.env.context.get('active_ids', [])
		data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
		data['form'] = self.read(['state_id'])[0]
		records = self.env[data['model']].browse(data.get('ids', []))
		return self.env['report'].get_action(records, 'realestate.report_property_per_location1', data=data)