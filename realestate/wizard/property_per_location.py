# -*- coding: utf-8 -*-

from odoo import models, fields, api


class property_per_location(models.TransientModel):

	_name = 'property.per.location'

	state_id = fields.Many2one("res.country.state", 'State')


	@api.multi
	def print_report(self):
		for data1 in self:
			data = data1.read([])[0]
		return self.env['report'].get_action(self,'realestate.report_property_per_location1', data)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: